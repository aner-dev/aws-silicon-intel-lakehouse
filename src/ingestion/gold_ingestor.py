import os
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from utils.logging_config import log


class GoldIngestor:
    def __init__(self, spark_session: SparkSession):
        self.spark = spark_session

    def write_to_snowflake(self, df, table_name: str):
        sf_options = {
            "sfURL": os.getenv("SNOWFLAKE_ACCOUNT_URL"),
            "sfUser": os.getenv("SNOWFLAKE_USER"),
            "sfPassword": os.getenv("SNOWFLAKE_PASSWORD"),
            "sfDatabase": "TAXI_ANALYTICS",
            "sfSchema": "GOLD",
            "sfWarehouse": "COMPUTE_WH",
        }
        log.info("exporting_to_snowflake", table=table_name)
        df.write.format("net.snowflake.spark.snowflake").options(**sf_options).option(
            "dbtable", table_name
        ).mode("overwrite").save()

    def run(self):
        log.info("gold_layer_process_started")

        # 1. GENERATE THE DATA
        performance_df = self.transform_taxi_performance()

        # 2. INTERNAL PERSISTENCE (Iceberg)
        log.info("writing_to_iceberg", table="fact_taxi_performance")
        performance_df.write.format("iceberg").mode("overwrite").saveAsTable(
            "glue_catalog.gold.fact_taxi_performance"
        )

        # 3. EXTERNAL EGRESS (Snowflake)
        self.write_to_snowflake(performance_df, "FACT_TAXI_PERFORMANCE")

        log.info("gold_layer_process_completed")

    def transform_taxi_performance(self):
        # 1. Load Silver Tables
        df_taxi = self.spark.table("glue_catalog.silver.nyc_taxi")
        df_zones = self.spark.table("glue_catalog.silver.dim_zones")

        # 2. Join
        gold_df = df_taxi.join(
            df_zones, df_taxi.PULocationID == df_zones.LocationID, "inner"
        ).select(
            df_zones.Borough,
            df_zones.Zone,
            df_taxi.fare_amount,
            df_taxi.tip_amount,
            df_taxi.tpep_pickup_datetime,
        )

        # 3. Aggregate
        performance_df = gold_df.groupBy("Borough", "Zone").agg(
            F.count("*").alias("total_trips"),
            F.sum("fare_amount").alias("revenue"),
            F.avg("tip_amount").alias("avg_tip"),
            F.max("tpep_pickup_datetime").alias("last_updated"),
        )

        # REFACTOR: Return the dataframe so 'run' can use it
        return performance_df


if __name__ == "__main__":
    from config.spark_setup import SparkSessionFactory

    spark = SparkSessionFactory.get_session()
    GoldIngestor(spark).run()
