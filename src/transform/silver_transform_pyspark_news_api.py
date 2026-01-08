import os
import structlog
from pyspark.sql import functions as F
from pyspark.sql.types import TimestampType
from config.spark_base import SparkSessionFactory  # Importamos tu Factory
from utils.logging_config import log


def transform_bronze_to_silver():
    # Usamos la Factory que ya tiene los configs de LocalStack y el fix de Hadoop
    spark = SparkSessionFactory.get_session()

    bronze_path = "s3a://silicon-intel-bronze/news_data_raw.json"

    log.info("starting_silver_transformation", source=bronze_path)

    try:
        # 1. Read Raw JSON
        raw_df = spark.read.option("multiline", "true").json(bronze_path)

        # 2. Transform (Explode & Flatten)
        silver_df = (
            raw_df.select(F.explode("articles").alias("article"))
            .select(
                F.col("article.source.name").alias("source_name"),
                F.col("article.author"),
                F.col("article.title"),
                F.col("article.description"),
                F.col("article.url"),
                F.col("article.publishedAt")
                .cast(TimestampType())
                .alias("published_at"),
                # column added only for partitioning (Optional)
                F.to_date("article.publishedAt").alias("event_date"),
                F.col("article.content"),
            )
            .filter((F.col("title") != "[Removed]") & (F.col("title").isNotNull()))
            .dropDuplicates(["title", "published_at"])
        )

        # 3. Write as Iceberg Table
        # 'local' is the name of the Catalog that was configured in the Factory
        table_name = "local.silver.news_articles"

        log.info("writing_to_iceberg", table=table_name)

        silver_df.writeTo(table_name).createOrReplace()

        log.info("transformation_success", row_count=silver_df.count())

    except Exception as e:
        log.error("transformation_failed", error=str(e))
        raise
    finally:
        spark.stop()


if __name__ == "__main__":
    transform_bronze_to_silver()
