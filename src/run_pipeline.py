import os
import yaml
from ingestion.bronze_ingestion_taxi import BronzeIngestor
from transform.silver_transform_pyspark_taxi import SilverIngestor
from utils.logging_config import log


def run_metadata_pipeline():
    # Load catalog once
    catalog_path = os.getenv("CATALOG_PATH", "src/config/catalog.yml")
    with open(catalog_path, "r") as f:
        catalog = yaml.safe_load(f)

    for source_id in catalog.keys():
        log.info("pipeline_started_for_source", source=source_id)

        try:
            # 1. BRONZE: Let the class handle its own 'skip' logic inside .run()
            # This keeps run_pipeline.py clean and DRY
            BronzeIngestor(source_id=source_id).run()

            # 2. SILVER: Already has a 'Defensive' check
            SilverIngestor(source_id=source_id).run()

            log.info("pipeline_success_for_source", source=source_id)

        except Exception as e:
            # Use 'continue' instead of 'raise' if it is wanted that
            # one source failure NOT to stop the others.
            log.error(
                "source_pipeline_critical_failure", source=source_id, error=str(e)
            )
            continue


if __name__ == "__main__":
    run_metadata_pipeline()
