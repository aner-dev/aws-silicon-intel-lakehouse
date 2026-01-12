# dag_silver_news.py
from airflow.decorators import dag, task
from datetime import datetime, timedelta
import os
import sys

# Add /usr/local/airflow/src to path to ensure imports work correctly
sys.path.append("/usr/local/airflow/src")

# Environment variables for Spark and Boto3 to communicate with LocalStack
# 'localstack' is used as the host since we are within the Docker network
ENV_VARS = {
    "AWS_ENDPOINT_URL": "http://localstack:4566",
    "AWS_ACCESS_KEY_ID": "test",
    "AWS_SECRET_ACCESS_KEY": "test",
    "AWS_DEFAULT_REGION": "us-east-1",
    "AWS_EC2_METADATA_DISABLED": "true",  # Evita que Spark tarde buscando credenciales de EC2
}


@dag(
    dag_id="silver_news_lakehouse_sync",
    default_args={
        "owner": "aner_dev",
        "retries": 1,
        "retry_delay": timedelta(minutes=5),
    },
    start_date=datetime(2026, 1, 9),
    schedule_interval="@hourly",
    catchup=False,
    tags=["lakehouse", "iceberg", "silver"],
)
def silver_news_sync():
    @task
    def ingest_to_bronze():
        """Extracts data from NewsAPI and persists it to S3 Bronze layer"""
        # Update environment variables for this specific task
        os.environ.update(ENV_VARS)
        from extract.bronze_ingestion_news_api import main

        return main()

    @task
    def transform_and_multiply():
        """Transforms Bronze data to Silver layer using Apache Iceberg"""
        os.environ.update(ENV_VARS)
        from utils.data_multiplier import run_multiplier

        input_path = "s3a://silicon-intel-bronze/bronze/news_api/*/*/*/*.json"
        output_table = "iceberg.silver.heavy_news_silver"

        # Execute with a representative workload for portfolio demonstration
        run_multiplier(input_path, output_table, iterations=1000)

    @task
    def validate_silver():
        """Executes data quality validations using Great Expectations"""
        os.environ.update(ENV_VARS)
        from quality.validate_silver import run_quality_checks

        run_quality_checks()

    # Workflow Dependency Definition
    ingest_to_bronze() >> transform_and_multiply() >> validate_silver()


# DAG Instantiation
silver_news_sync()
