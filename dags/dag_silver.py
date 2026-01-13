from airflow.sdk import dag, task
from airflow import Dataset
from src.transform.silver_transform_pyspark_taxi import SilverIngestor
from datetime import datetime

BRONZE_DATA = Dataset("s3://bronze/nyc_taxi")
SILVER_DATA = Dataset("iceberg://silver/taxi_tables")


@dag(
    schedule=[BRONZE_DATA],  # Triggers when Bronze finishes
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["medallion", "silver"],
)
def silver_transformation():
    @task(outlets=[SILVER_DATA])
    def transform_to_iceberg(source: str):
        SilverIngestor(source_id=source).run()

    transform_to_iceberg("yellow_taxi")


silver_transformation()
