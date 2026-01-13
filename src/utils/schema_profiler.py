import json
from config.spark_setup import SparkSessionFactory
from utils.observability import log_job_status
from utils.logging_config import log


class SchemaProfiler:
    def __init__(self):
        self.spark = SparkSessionFactory.get_session()
        # Define tables here so 'self.tables' exists throughout the class
        self.tables = ["glue_catalog.silver.nyc_taxi", "glue_catalog.silver.dim_zones"]

    def profile_silver_layer(self):
        """
        Inspects Silver tables and logs the results to the
        DynamoDB audit table via log_job_status.
        """
        # Fix: Now self.tables is a valid attribute
        log.info("discovery_started", target_tables=self.tables)

        for table_name in self.tables:
            try:
                # 1. Check if the table actually exists in the catalog
                if self.spark.catalog.tableExists(table_name):
                    df = self.spark.table(table_name)

                    # 2. Extract Metadata
                    metadata = {"columns": df.columns, "row_count": df.count()}

                    # 3. Persist to DynamoDB via your observability utility
                    log_job_status(
                        job_id=f"discovery_{table_name}",
                        status="COMPLETED",
                        details=json.dumps(metadata),
                    )

                    log.info("discovery_recorded_in_audit", table=table_name)
                else:
                    # If this triggers, we need to check the SilverIngestor execution
                    log.warning(
                        "discovery_table_missing",
                        table=table_name,
                        hint="Verify if SilverIngestor has been run.",
                    )

            except Exception as e:
                log.error("discovery_failed", table=table_name, error=str(e))


if __name__ == "__main__":
    profiler = SchemaProfiler()
    profiler.profile_silver_layer()
