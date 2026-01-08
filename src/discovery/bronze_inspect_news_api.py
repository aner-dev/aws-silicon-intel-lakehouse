# bronze_inspect_news_api.py

from config.spark_base import SparkSessionFactory
from utils.logging_config import log


def main():
    log.info("discovery_process_initiated", stage="bronze", source="s3")

    try:
        # 1. Get the session using our Factory
        spark = SparkSessionFactory.get_session()

        # 2. Define the Bronze path (LocalStack S3)
        # Adjust this path to the one you are using for your NewsAPI JSON files
        bronze_path = "s3a://silicon-intel-bronze/news-data/"

        log.info("reading_bronze_layer", path=bronze_path)

        # 3. Exploratory reading
        # We use .option("recursiveFileLookup", "true") in case there are partitions
        df = spark.read.format("json").load(bronze_path)

        # 4. Schema Diagnostics
        log.info("schema_discovery")
        df.printSchema()

        # Display the first 5 records to validate content
        df.show(5, truncate=False)

        log.info("discovery_process_completed", total_records=df.count())

    except Exception as e:
        log.error("discovery_process_failed", error=str(e), exc_info=True)
    finally:
        # It is good practice to close the session in inspection scripts
        if "spark" in locals():
            spark.stop()
            log.info("spark_session_stopped")


if __name__ == "__main__":
    main()
