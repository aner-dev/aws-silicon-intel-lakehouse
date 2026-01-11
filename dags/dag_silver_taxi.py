from airflow.decorators import dag, task
from airflow.datasets import Dataset  # The "Senior" way to decouple
from datetime import datetime, timedelta
import os
import sys

# Reference to the Bronze Data - The Silver DAG waits for this
BRONZE_TAXI_DATA = Dataset("s3://silicon-intel-bronze/nyc_taxi/")


@dag(
    dag_id="silver_taxi_iceberg_sync",
    default_args={
        "owner": "aner_dev",
        "retries": 1,
    },
    start_date=datetime(2026, 1, 11),
    schedule=[BRONZE_TAXI_DATA],  # Reactive: Triggers when Bronze finishes
    catchup=False,
    tags=["aws", "iceberg", "lakehouse"],
)
def silver_taxi_sync():
    @task
    def spark_transform_to_iceberg():
        """
        Reads from Bronze S3 and writes to Silver Iceberg Table.
        This demonstrates ACID transactions on Object Storage.
        """
        from transform.silver_transform_pyspark_taxi import run_spark_job

        # In a real AWS scenario, we would use a Glue Catalog
        # In LocalStack, we use the Iceberg REST catalog or Hadoop catalog
        run_spark_job(
            input_uri="s3a://silicon-intel-bronze/nyc_taxi/*.parquet",
            output_table="iceberg.silver.taxi_trips",
        )

    @task
    def generate_silver_metrics():
        """Aggregates data for the Gold Layer trigger"""
        print("Calculating trip durations and fare averages...")

    spark_transform_to_iceberg() >> generate_silver_metrics()


silver_taxi_sync()
