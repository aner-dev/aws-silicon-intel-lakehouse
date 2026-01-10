# silver_transform_pyspark_taxi.py
from datetime import datetime
from pyspark.sql import functions as F
from config.spark_setup import SparkSessionFactory
from utils.logging_config import log


def transform_taxi_bronze_to_silver(processing_date: str | None = None):
    if not processing_date:
        processing_date = datetime.now().strftime("%Y-%m-%d")

    bucket = "silicon-intel-bronze"
    table_name = "iceberg.silver.nyc_taxi"
    # 1. PATH TARGETING (Using the Hive standard we set)
    # Note: We point to the category folder and the specific ingestion date
    bronze_path = f"s3a://{bucket}/bronze/nyc_taxi/year=*/month=*/*.parquet"  # INCREMENTAL PROCESSING

    spark = SparkSessionFactory.get_session()

    try:
        log.info("starting_amazon_silver_transformation", source=bronze_path)

        # 2. READ (Optimized: Only read columns we need to save RAM)
        df = spark.read.parquet(bronze_path)

        # 3. TRANSFORM: Explicitly cast to resolve the BIGINT vs INT conflict
        silver_df = (
            df.filter("trip_distance > 0")
            .filter("VendorID IS NOT NULL")
            .select(
                # We cast everything to the "Silver" standard here.
                # 'long' handles both INT and BIGINT from the source.
                F.col("VendorID").cast("long").alias("vendor_id"),
                F.col("tpep_pickup_datetime").alias("pickup_time"),
                F.col("tpep_dropoff_datetime").alias("dropoff_time"),
                F.col("passenger_count").cast("int"),
                F.col("trip_distance").cast("double"),
                F.col("total_amount").cast("double"),
                F.lit(processing_date).alias("ingested_at"),
            )
            .distinct()
        )

        # 4. LOAD WITH ICEBERG OPTIMIZATION
        if not spark.catalog.tableExists(table_name):
            log.info("creating_new_iceberg_table", table=table_name)
            # 🟢 PARTITION STRATEGY: Iceberg Hidden Partitioning (Monthly)
            # This optimizes queries that filter by time without needing extra columns.
            silver_df.writeTo(table_name).tableProperty(
                "write.format.default", "parquet"
            ).partitionedBy(F.months("pickup_time")).create()
        else:
            log.info("merging_into_existing_table", table=table_name)
            silver_df.createOrReplaceTempView("source_taxi")

            # 🟢 IDEMPOTENCY: MERGE (Update existing or Insert new)
            # This ensures that running the same script twice won't create duplicates.
            spark.sql(f"""
                MERGE INTO {table_name} t
                USING source_taxi s
                ON t.vendor_id = s.vendor_id AND t.pickup_time = s.pickup_time
                WHEN MATCHED THEN UPDATE SET *
                WHEN NOT MATCHED THEN INSERT *
            """)
            # Refactor: Adding a 'source_taxi.pickup_time > ...' filter here
            # can help Iceberg "Prune" partitions and go faster.

        log.info("nyc_taxi_silver_success", table=table_name)

    except Exception as e:
        log.error("nyc_taxi_silver_failed", error=str(e))
        raise e


if __name__ == "__main__":
    transform_taxi_bronze_to_silver()
