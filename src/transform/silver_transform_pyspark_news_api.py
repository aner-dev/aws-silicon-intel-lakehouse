# silver_transform_pyspark_news_api.py

import os
import boto3
from datetime import datetime
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    ArrayType,
    TimestampType,
)
from pyspark.sql.utils import AnalysisException
from botocore.exceptions import ClientError
from pyspark.errors import PySparkException
from config.spark_setup import SparkSessionFactory
from utils.logging_config import log

# 1. Schema Definition (Schema Enforcement)
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


def log_audit_dynamo(status, table_name, record_count=0):
    """Registers the job result in the audit table."""
    dynamo = boto3.resource(
        "dynamodb", endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    )
    table = dynamo.Table("pipeline_audit")
    table.put_item(
        Item={
            "job_id": f"silver_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "status": status,
            "table_target": table_name,
            "record_count": record_count,
            "timestamp": datetime.now().isoformat(),
            "layer": "silver",
        }
    )


def check_s3_files(bucket, prefix):
    """Pre-validation in S3 before starting Spark."""
    s3 = boto3.client(
        "s3", endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    )
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return "Contents" in response


def transform_articles(df):
    """Business Logic: Cleaning and structuring."""
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
    """Upsert Logic (MERGE) specific to Apache Iceberg."""
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
            WHEN MATCHED THEN UPDATE SET *
            WHEN NOT MATCHED THEN INSERT *
        """)


def transform_bronze_to_silver():
    """Silver Layer Orchestrator."""
    bucket = "silicon-intel-bronze"
    table_name = "iceberg.silver.news_articles"

    if not check_s3_files(bucket, "bronze/news_api/"):
        log.warn("no_files_found_in_bronze", bucket=bucket)
        return

    spark = SparkSessionFactory.get_session()
    # Captures all partitioned JSON files
    bronze_path = f"s3a://{bucket}/bronze/news_api/*/*/*/*.json"

    try:
        log.info("starting_silver_transformation", source=bronze_path)

        # EXTRACT
        raw_df = (
            spark.read.option("multiline", "true").schema(NEWS_SCHEMA).json(bronze_path)
        )
        if raw_df.isEmpty():
            log.warn("source_data_empty", path=bronze_path)
            return

        # TRANSFORM
        transformed_df = transform_articles(raw_df)
        count = transformed_df.count()

        # LOAD
        upsert_to_iceberg(spark, transformed_df, table_name)

        # AUDIT
        log_audit_dynamo("SUCCESS", table_name, record_count=count)
        log.info("transformation_success", table=table_name, count=count)

    except AnalysisException as ae:
        # SQL errors, Schema or Tables not founded
        log.error("schema_or_sql_error", error=str(ae), table=table_name)
        log_audit_dynamo("FAILED_SCHEMA", table_name)
        raise ae
    except ClientError as ce:
        # AWS-specific errors (S3/Dynamo)
        log.error("aws_service_error", error=str(ce))
        # We don't trigger log_audit_dynamo here because Dynamo likely failed
        raise ce

    except PySparkException as pe:
        # Internal Spark execution errors (JVM, Memory, etc.)
        log.error("spark_runtime_error", error=str(pe))
        log_audit_dynamo("FAILED_SPARK", table_name)
        raise pe

    except Exception as e:
        log.error("silver_transformation_failed", error=str(e))
        log_audit_dynamo("FAILED", table_name)
        raise e


if __name__ == "__main__":
    transform_bronze_to_silver()
