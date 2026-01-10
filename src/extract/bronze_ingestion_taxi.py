import requests
import boto3
from utils.logging_config import log


def ingest_taxi_range(years=["2023", "2024"], months=None):
    if months is None:
        months = [f"{m:02d}" for m in range(1, 13)]

    # We only need the local S3 client now
    s3_local = boto3.client("s3", endpoint_url="http://localhost:4566")

    base_url = "https://d37ci6vzurychx.cloudfront.net/trip-data"
    bucket_local = "silicon-intel-bronze"

    log.info("starting_taxi_ingestion_job", years=years, total_months=len(months))

    for year in years:
        for month in months:
            file_name = f"yellow_tripdata_{year}-{month}.parquet"
            source_url = f"{base_url}/{file_name}"
            dest_key = f"bronze/nyc_taxi/year={year}/month={month}/taxi_data.parquet"

            try:
                log.info("downloading_file", url=source_url)

                with requests.get(source_url, stream=True) as r:
                    r.raise_for_status()
                    s3_local.upload_fileobj(r.raw, bucket_local, dest_key)

                log.info("ingestion_success", key=dest_key)

            except Exception as e:
                log.error("ingestion_failed", url=source_url, error=str(e))


# CRITICAL: This is what was missing!
if __name__ == "__main__":
    ingest_taxi_range()

