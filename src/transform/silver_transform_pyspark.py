# silver_transform_pypsark.py
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql.types import StructType, StructField, StringType, TimestampType
import os
from utils.logging_config import setup_logging
import structlog

log = structlog.get_logger()


def create_spark_session():
    """Builds a SparkSession with strict overrides to fix duration string errors."""
    spark = (
        SparkSession.builder.appName("NewsBronzeToSilver")
        .config("spark.jars.packages", "org.apache.hadoop:hadoop-aws:3.3.4")
        # You can actually set Hadoop configs directly in the builder using this prefix:
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config(
            "spark.hadoop.fs.s3a.endpoint",
            os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
        )
        .config("spark.hadoop.fs.s3a.access.key", "test")
        .config("spark.hadoop.fs.s3a.secret.key", "test")
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config(
            "spark.hadoop.fs.s3a.aws.credentials.provider",
            "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
        )
        # THE FIXES: Using 'spark.hadoop.' prefix tells Spark to pass these to Hadoop
        .config("spark.hadoop.fs.s3a.connection.timeout", "60000")
        .config("spark.hadoop.fs.s3a.connection.establish.timeout", "60000")
        .config("spark.hadoop.fs.s3a.multipart.purge.age", "86400")  # Fixes '24h'
        .config("spark.hadoop.fs.s3a.metadata.ttl", "60000")
        .config("spark.hadoop.fs.s3a.connection.timeout", "60000")
        .config("spark.hadoop.fs.s3a.connection.establish.timeout", "60000")
        .config("spark.hadoop.fs.s3a.threads.keepalivetime", "60")  # Add this!
        .config("spark.hadoop.fs.s3a.impl.disable.cache", "true")  # Add this!
        .getOrCreate()
    )
    return spark


def transform_bronze_to_silver():
    setup_logging()
    spark = create_spark_session()

    bronze_path = "s3a://silicon-intel-bronze/news_data_raw.json"
    silver_path = "s3a://silicon-intel-silver/articles_parquet"

    log.info("starting_transformation", source=bronze_path, target=silver_path)

    # 1. Read JSON (Spark reads the whole file as one row initially because of the NewsAPI structure)
    raw_df = spark.read.option("multiline", "true").json(bronze_path)

    # 2. Explode the 'articles' array into rows
    # JSON flattening (semi-structured data)
    df_exploded = raw_df.select(F.explode("articles").alias("article"))

    # 3. Flatten and Clean
    silver_df = (
        df_exploded.select(
            F.col("article.source.name").alias("source_name"),
            F.col("article.author"),
            F.col("article.title"),
            F.col("article.description"),
            F.col("article.url"),
            # Cast string to proper Timestamp
            F.col("article.publishedAt").cast(TimestampType()).alias("published_at"),
            F.col("article.content"),
        )
        .filter(
            # Filter out 'Removed' articles
            (F.col("title") != "[Removed]") & (F.col("title").isNotNull())
        )
        .dropDuplicates(["title", "published_at"])
    )

    # 4. Write as Parquet (Partitioned by Date)
    silver_df.write.mode("overwrite").parquet(silver_path)

    log.info("transformation_success", row_count=silver_df.count())
    spark.stop()


if __name__ == "__main__":
    transform_bronze_to_silver()
