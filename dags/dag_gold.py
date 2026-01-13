from airflow.sdk import dag, task
from airflow import Dataset
from gold_ingestion import GoldIngestor
from config.spark_setup import SparkSessionFactory
from datetime import datetime

SILVER_DATA = Dataset("iceberg://silver/taxi_tables")


@dag(
    schedule=[SILVER_DATA],
    start_date=datetime(2024, 1, 1),
    catchup=False,
    tags=["medallion", "gold"],
)
def gold_snowflake_egress():
    @task
    def process_gold_and_egress():
        spark = SparkSessionFactory.get_session()
        GoldIngestor(spark).run()

    process_gold_and_egress()


gold_snowflake_egress()
