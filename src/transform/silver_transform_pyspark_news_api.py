# silver_transform_pyspark_news_api.py
import os
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    ArrayType,
    TimestampType,
)
from pyspark.sql.utils import AnalysisException
import boto3

from config.spark_base import SparkSessionFactory
from utils.logging_config import log

# 1. Schema Enforcement definition
NEWS_SCHEMA = StructType(
    [
        StructField(
            "articles",
            ArrayType(
                StructType(
                    [
                        StructField(
                            "source", StructType([StructField("name", StringType())])
                        ),
                        StructField("author", StringType()),
                        StructField("title", StringType()),
                        StructField("description", StringType()),
                        StructField("url", StringType()),
                        StructField("publishedAt", StringType()),
                        StructField("content", StringType()),
                    ]
                )
            ),
        )
    ]
)


def check_s3_files(bucket, prefix):
    """Pre-validation without Spark to save resources."""
    s3 = boto3.client(
        "s3", endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    )
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return "Contents" in response


def transform_articles(df):
    """
    BUSINESS LOGIC ONLY.
    Input: raw_df -> Output: transformed_df
    """
    return (
        df.select(F.explode("articles").alias("article"))
        .select(
            F.col("article.source.name").alias("source_name"),
            F.col("article.author"),
            F.col("article.title").alias("title"),
            F.col("article.url").alias("url"),
            F.col("article.publishedAt").cast(TimestampType()).alias("published_at"),
            F.to_date("article.publishedAt").alias("event_date"),
            F.col("article.content"),
        )
        .withColumn("processed_at", F.current_timestamp())
        .filter("title IS NOT NULL AND title != '[Removed]'")
        .dropDuplicates(["title", "published_at"])
    )


def upsert_to_iceberg(spark, df, table_name, partition_col="event_date"):
    """Handles the Iceberg-specific MERGE logic."""
    if not spark.catalog.tableExists(table_name):
        log.info("creating_new_iceberg_table", table=table_name)
        df.writeTo(table_name).partitionedBy(partition_col).create()
    else:
        log.info("performing_iceberg_merge", table=table_name)
        df.createOrReplaceTempView("source_data")
        spark.sql(f"""
            MERGE INTO {table_name} t
            USING source_data s
            ON t.title = s.title AND t.published_at = s.published_at
            WHEN MATCHED THEN 
                UPDATE SET *
            WHEN NOT MATCHED THEN 
                INSERT *
        """)


def transform_bronze_to_silver():
    """Orchestration Function (The Entry Point)"""
    bucket = "silicon-intel-bronze"
    table_name = "local.silver.news_articles"

    # 1. Infrastructure Check
    if not check_s3_files(bucket, ""):
        log.warn("no_files_found_in_bronze", bucket=bucket)
        return

    spark = SparkSessionFactory.get_session()
    bronze_path = f"s3a://{bucket}/*.json"

    try:
        # 2. Extract
        raw_df = (
            spark.read.option("multiline", "true").schema(NEWS_SCHEMA).json(bronze_path)
        )

        if raw_df.isEmpty():
            log.warn("source_data_empty", path=bronze_path)
            return

        # 3. Transform
        log.info("transforming_data", source=bronze_path)
        transformed_df = transform_articles(raw_df)

        # 4. Load
        upsert_to_iceberg(spark, transformed_df, table_name)
        log.info("transformation_success", table=table_name)

    except AnalysisException as ae:
        log.error("schema_or_sql_error", error=str(ae), table=table_name)
        raise ae
    except Exception as e:
        log.error("unexpected_transformation_error", error=str(e))
        raise e


if __name__ == "__main__":
    transform_bronze_to_silver()
