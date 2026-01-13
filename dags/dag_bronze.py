from airflow.sdk import task, dag
from airflow import Dataset
from datetime import datetime
from src.ingestion.bronze_ingestion_taxi import BronzeIngestor

BRONZE_DATA = Dataset("s3://bronze/nyc_taxi")


@dag(
    start_date=datetime(2024, 1, 1),
    schedule="@monthly",
    catchup=False,
    tags=["medallion", "bronze"],
)
def bronze_ingestion():
    @task(outlets=[BRONZE_DATA])
    def ingest_taxi_data(source: str):
        BronzeIngestor(source_id=source).run()

    ingest_taxi_data("yellow_taxi")


bronze_ingestion()

