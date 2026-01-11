import requests
import boto3
import uuid
from utils.observability import log_job_status, notify_failure
from utils.logging_config import log


def ingest_taxi_range(years=["2024"], months=["01"]):
    s3_local = boto3.client("s3", endpoint_url="http://localhost:4566")
    bucket_local = "silicon-intel-bronze"
    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"

    for year in years:
        for month in months:
            job_id = f"taxi-ingest-{year}-{month}-{uuid.uuid4().hex[:4]}"
            file_name = f"yellow_tripdata_{year}-{month}.parquet"
            source_url = f"{base_url}/{file_name}"
            dest_key = f"bronze/nyc_taxi/year={year}/month={month}/data.parquet"

            try:
                # 1. Log Start
                log_job_status(job_id, "STARTED", f"Ingesting {file_name}")

                # 2. Execute Streaming Download
                with requests.get(source_url, stream=True) as r:
                    r.raise_for_status()
                    s3_local.upload_fileobj(r.raw, bucket_local, dest_key)

                # 3. Log Success
                log_job_status(job_id, "SUCCESS", f"Landed at {dest_key}")
                log.info("ingestion_complete", key=dest_key)

            except Exception as e:
                # 4. Notify Failure (SNS -> SQS) and Log
                error_msg = str(e)
                log_job_status(job_id, "FAILED", error_msg)
                notify_failure(job_id, error_msg)


if __name__ == "__main__":
    ingest_taxi_range()
