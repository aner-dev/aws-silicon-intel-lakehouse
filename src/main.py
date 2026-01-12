import yaml
import boto3
from transform.silver_transform_pyspark_taxi import SilverIngestor

# from extract.bronze_taxi import BronzeExtractor  <-- Assume this exists
from utils.logging_config import log


def check_s3_path_exists(bucket, prefix):
    s3 = boto3.client("s3")
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix, MaxKeys=1)
    return "Contents" in resp


def run_metadata_pipeline():
    with open("src/config/catalog.yml", "r") as f:
        catalog = yaml.safe_load(f)

    for source_id, config in catalog.items():
        # 1. SMART CHECK: Do we need to run Bronze?
        bronze_path = config.get("source_path")
        if not check_s3_path_exists("silicon-intel-bronze", bronze_path):
            log.info("bronze_missing_starting_extraction", source=source_id)
            # BronzeExtractor(source_id).run()
        else:
            log.info("bronze_data_found_skipping_extraction", source=source_id)

        # 2. RUN SILVER
        try:
            ingestor = SilverIngestor(source_id=source_id)
            ingestor.run()
        except Exception as e:
            log.error("silver_failed", source=source_id, error=str(e))
            raise e
