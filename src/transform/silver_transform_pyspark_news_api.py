from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    ArrayType,
    TimestampType,
)
from pyspark.sql.utils import AnalysisException
from config.spark_base import SparkSessionFactory
from utils.logging_config import log
import boto3
import os

# 1. Explicit definition (Schema Enforcement)
# This guarantees that Spark doesn't have to infer the schema.
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
    """Pro Check: Pre-validation without Spark"""
    s3 = boto3.client(
        "s3", endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    )
    response = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    return "Contents" in response


def transform_bronze_to_silver():
    # Pre-Spark Check
    bucket = "silicon-intel-bronze"
    if not check_s3_files(bucket, ""):
        log.warn("no_files_found_in_bronze", bucket=bucket)
        return

    spark = SparkSessionFactory.get_session()

    # 1. Dynamic Path (Avoiding reading ALL the bucket each time)
    # In production, the date will be passed as argument of the script
    from datetime import datetime

    today = datetime.now().strftime("%Y-%m-%d")

    bronze_path = f"s3a://{bucket}/*.json"
    log.info("starting_transformation", processing_date=today, source=bronze_path)

    try:
        raw_df = (
            spark.read.option("multiline", "true").schema(NEWS_SCHEMA).json(bronze_path)
        )

        # Preventive Validation:
        if raw_df.isEmpty():
            log.warn("source_data_empty", path=bronze_path)
            return
        # Transformation (Explode & Flatten)
        transformed_df = (
            raw_df.select(F.explode("articles").alias("article"))
            .select(
                F.col("article.source.name").alias("source_name"),
                F.col("article.author"),
                F.col("article.title").alias("title"),
                F.col("article.url").alias("url"),
                F.col("article.publishedAt")
                .cast(TimestampType())
                .alias("published_at"),
                F.to_date("article.publishedAt").alias("event_date"),
                F.col("article.content"),
            )
            .withColumn(
                "processed_at", F.current_timestamp()
            )  # Timestamp to know WHEN it INSERT/UPDATE
            .filter(
                "title IS NOT NULL AND title != '[Removed]'"
            )  # Sintaxis SQL es más limpia
            .dropDuplicates(["title", "published_at"])
        )

        table_name = "local.silver.news_articles"

        # 2. Iceberg Partitioning (Using 'event_date')
        # Usamos partitionBy para que las queries por fecha sean ultra rápidas
        log.info("writing_to_iceberg_partitioned", table=table_name)

        # 3. Best Practice: MERGE INTO (Upsert)
        # Si la tabla no existe, la creamos. Si existe, hacemos MERGE.
        if not spark.catalog.tableExists(table_name):
            log.info("creating_new_iceberg_table", table=table_name)
            transformed_df.writeTo(table_name).partitionedBy("event_date").create()
        else:
            log.info("performing_iceberg_merge", table=table_name)
            # This avoid historic duplicates comparing title & date
            transformed_df.createOrReplaceTempView("source_data")

            spark.sql(f"""
                MERGE INTO {table_name} t
                USING source_data s
                ON t.title = s.title AND t.published_at = s.published_at
                WHEN MATCHED THEN 
                    UPDATE SET * -- Update all the values if title & date MATCH
                WHEN NOT MATCHED THEN 
                    INSERT * -- Inserta si es un registro totalmente nuevo
            """)

        log.info("transformation_success", table=table_name)

    except AnalysisException as ae:
        # Errores de SQL, columnas faltantes o tablas no encontradas
        log.error("schema_or_sql_error", error=str(ae), table=table_name)
        raise ae
    except Exception as e:
        # Cualquier otro error (red, memoria, etc.)
        log.error("unexpected_transformation_error", error=str(e))
        raise e
