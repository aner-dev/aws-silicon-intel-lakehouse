# silver_transform_pyspark_taxi.py
import os
import yaml
import uuid
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
        self.bucket = os.getenv("BRONZE_BUCKET", "aws-mobility-elt-pipeline-bronze")

    def _load_catalog(self) -> dict:
        with open("config/catalog.yaml", "r") as f:
            return yaml.safe_load(f)

    def _check_source_exists(self, path: str) -> bool:
        """Verifies if the S3 path has data to prevent Spark empty-read errors."""
        try:
            # We use the Spark session's Hadoop configuration
            # to check the file system without loading data
            sc = self.spark.sparkContext
            Path = sc._gateway.jvm.org.apache.hadoop.fs.Path
            FileSystem = sc._gateway.jvm.org.apache.hadoop.fs.FileSystem
            conf = sc._jsc.hadoopConfiguration()

            fs = FileSystem.get(conf)
            return fs.exists(Path(path))
        except Exception:
            return False

    def run(self, execution_id: str | None = None, processing_date: str | None = None):
        job_name = f"{self.source_id}_silver_ingest"
        proc_date = processing_date or datetime.now().strftime("%Y-%m-%d")
        exec_id = execution_id or str(uuid.uuid4())
        exec_timestamp = datetime.now().isoformat()

        # 1. Define once at the top
        source_full_path = f"s3a://{self.bucket}/{self.config['source_path']}"

        # 2. Defensive Check (Pre-flight)
        if not self._check_source_exists(source_full_path):
            log.warning("source_data_not_found", path=source_full_path)
            log_job_status(
                job_name=job_name,
                status="SKIPPED",
                execution_id=exec_id,
                details="No source files found.",
            )
            return

        # 2. Log START only if data exists
        log_job_status(
            job_name=job_name,
            status="STARTED",
            execution_id=exec_id,
            details=f"Source: {self.source_id}",
        )

        try:
            # NO NEED to redefine source_full_path here anymore
            log.info("extracting_bronze_data", path=source_full_path)
            # In silver_transform_pyspark_taxi.pyspark
            file_format = self.config.get(
                "format", "parquet"
            )  # Default to parquet if not specified
            df = self.spark.read.format(file_format).load(source_full_path)

            # 1. Dynamic Transformation (Rename & Select)
            select_expr = [
                F.col(src).alias(tgt) for tgt, src in self.config["mappings"].items()
            ]

            # Data Lineage
            silver_df = (
                df.select(*select_expr)
                .withColumn("ingested_at", F.lit(proc_date))  # Business Date
                .withColumn("execution_id", F.lit(exec_id))  # Unique Trace ID
                .withColumn("processed_at", F.lit(exec_timestamp))  # System Timestamp
                .withColumn("_source_file", F.input_file_name())
                .distinct()
            )

            # 3. CAPTURE METRICS (The missing piece)
            row_count = silver_df.count()

            # Schema Evolution & Table Initialization
            self._ensure_table_exists(silver_df)

            # 3. Idempotent Load (MERGE)
            self._upsert_to_iceberg(silver_df)

            log_job_status(
                job_name=job_name,
                status="SUCCESS",
                execution_id=exec_id,
                metrics={"rows_processed": row_count},  # Injected metrics
                details=f"Target: {self.config['target_table']}",
            )

        except Exception as e:
            log.error("silver_ingestion_failed", source=self.source_id, error=str(e))
            log_job_status(
                job_name=job_name, status="FAILED", execution_id=exec_id, details=str(e)
            )
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
