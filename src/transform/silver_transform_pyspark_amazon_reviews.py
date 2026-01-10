from datetime import datetime
from pyspark.sql import functions as F
from config.spark_setup import SparkSessionFactory
from utils.logging_config import log


def transform_reviews_bronze_to_silver(processing_date: str | None = None):
    if not processing_date:
        processing_date = datetime.now().strftime("%Y-%m-%d")

    bucket = "silicon-intel-bronze"
    table_name = "iceberg.silver.amazon_reviews"

    # 1. PATH TARGETING (Using the Hive standard we set)
    # Note: We point to the category folder and the specific ingestion date
    bronze_path = f"s3a://{bucket}/bronze/amazon_reviews/Electronics/product_category=Electronics/*.parquet"

    spark = SparkSessionFactory.get_session()

    try:
        log.info("starting_amazon_silver_transformation", source=bronze_path)

        # 2. EXTRACT (Schema is automatic with Parquet)
        df = spark.read.parquet(bronze_path)

        # 3. TRANSFORM (Standardizing columns for Silver)
        silver_df = df.select(
            F.col("review_id"),
            F.col("customer_id"),
            F.col("star_rating").cast("int").alias("rating"),
            F.col("review_headline").alias("headline"),
            F.col("review_body").alias("content"),
            F.to_date("review_date").alias("review_date"),
            F.lit(processing_date).alias("ingested_at"),
        ).filter("content IS NOT NULL")

        # 4. LOAD (Iceberg Upsert)
        if not spark.catalog.tableExists(table_name):
            silver_df.writeTo(table_name).partitionedBy("review_date").create()
        else:
            silver_df.createOrReplaceTempView("source_reviews")
            spark.sql(f"""
                MERGE INTO {table_name} t
                USING source_reviews s
                ON t.review_id = s.review_id
                WHEN MATCHED THEN UPDATE SET *
                WHEN NOT MATCHED THEN INSERT *
            """)

        log.info("amazon_silver_success", table=table_name)

    except Exception as e:
        log.error("amazon_silver_failed", error=str(e))
        raise e


if __name__ == "__main__":
    transform_reviews_bronze_to_silver()
