import os
import yaml
from datetime import datetime
from pyspark.sql import functions as F
from config.spark_setup import SparkSessionFactory
from utils.observability import notify_failure, log_job_status
from utils.logging_config import log


class SilverIngestor:
    def __init__(self, source_id: str):
        self.source_id = source_id
        self.config = self._load_catalog()[source_id]
        self.spark = SparkSessionFactory.get_session()
        self.bucket = os.getenv("BRONZE_BUCKET", "silicon-intel-bronze")

    def _load_catalog(self) -> dict:
        with open("config/catalog.yaml", "r") as f:
            return yaml.safe_load(f)

    def run(self, processing_date: str | None = None):
        """
        Executes the Bronze to Silver transformation pipeline.
        The processing_date is optional; defaults to today's date if None.
        """
        job_name = f"{self.source_id}_silver_ingest"
        proc_date = processing_date or datetime.now().strftime("%Y-%m-%d")

        log_job_status(
            job_id=job_name, status="STARTED", details=f"Source: {self.source_id}"
        )

        try:
            source_full_path = f"s3a://{self.bucket}/{self.config['source_path']}"
            log.info("extracting_bronze_data", path=source_full_path)

            df = self.spark.read.parquet(source_full_path)

            # 1. Dynamic Transformation (Rename & Select)
            select_expr = [
                F.col(src).alias(tgt) for tgt, src in self.config["mappings"].items()
            ]

            silver_df = (
                df.select(*select_expr)
                .withColumn("ingested_at", F.lit(proc_date))
                .distinct()
            )

            # 2. Schema Evolution & Table Initialization
            self._ensure_table_exists(silver_df)

            # 3. Idempotent Load (MERGE)
            self._upsert_to_iceberg(silver_df)

            log_job_status(
                job_id=job_name,
                status="SUCCESS",
                details=f"Target: {self.config['target_table']}",
            )

        except Exception as e:
            log.error("silver_ingestion_failed", source=self.source_id, error=str(e))
            log_job_status(job_id=job_name, status="FAILED", details=str(e))
            notify_failure(job_name=job_name, error_message=str(e))
            raise e

    def _ensure_table_exists(self, df):
        table = self.config["target_table"]
        partition_col = self.config["partition_by"]

        if not self.spark.catalog.tableExists(table):
            log.info("initializing_iceberg_table", table=table)
            df.writeTo(table).tableProperty(
                "write.format.default", "parquet"
            ).partitionedBy(F.months(partition_col)).create()

    def _upsert_to_iceberg(self, df):
        table = self.config["target_table"]
        merge_keys = self.config["merge_keys"]

        # Build the dynamic JOIN condition
        join_condition = " AND ".join([f"t.{k} = s.{k}" for k in merge_keys])

        df.createOrReplaceTempView("source_view")

        self.spark.sql(f"""
            MERGE INTO {table} t
            USING source_view s
            ON {join_condition}
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
        """)


if __name__ == "__main__":
    # Example execution
    SilverIngestor(source_id="yellow_taxi").run()
