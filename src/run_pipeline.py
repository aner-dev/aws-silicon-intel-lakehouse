import yaml
import boto3
from extract.bronze_ingestion_taxi import BronzeIngestor
from transform.silver_transform_pyspark_taxi import SilverIngestor
from utils.logging_config import log


def check_s3_path_exists(bucket, prefix):
    """Checks if data already exists to avoid redundant downloads."""
    s3 = boto3.client("s3", endpoint_url="http://localhost:4566")
    # Clean the prefix of wildcards for the check
    search_prefix = prefix.split("*")[0]
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=search_prefix, MaxKeys=1)
    return "Contents" in resp


def run_metadata_pipeline():
    with open("src/config/catalog.yml", "r") as f:
        catalog = yaml.safe_load(f)

    for source_id, config in catalog.items():
        log.info("processing_source", source=source_id)

        # 1. BRONZE LAYER (Extraction)
        bronze_path = config.get("source_path")
        if not check_s3_path_exists("silicon-intel-bronze", bronze_path):
            log.info("extracting_raw_data", source=source_id)
            bronze = BronzeIngestor(source_id=source_id)
            bronze.run()
        else:
            log.info("raw_data_exists_skipping_bronze", source=source_id)

        # 2. SILVER LAYER (Transformation)
        try:
            log.info("transforming_to_silver", source=source_id)
            silver = SilverIngestor(source_id=source_id)
            silver.run()
        except Exception as e:
            log.error("pipeline_failed", source=source_id, error=str(e))
            raise e


if __name__ == "__main__":
    run_metadata_pipeline()
