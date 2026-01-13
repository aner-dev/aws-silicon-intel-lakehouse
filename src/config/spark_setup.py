import os
from pyspark.sql import SparkSession

from utils.logging_config import log

AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
PROJECT_NAME = os.getenv("PROJECT_NAME", "aws-mobility-elt-pipeline-lakehouse")


class SparkSessionFactory:
    @staticmethod
    def get_session():
        try:
            log.info(
                "spark_session_request", catalog="iceberg_hadoop", project=PROJECT_NAME
            )

            builder = (
                SparkSession.builder.appName(f"{PROJECT_NAME}-Lakehouse")
                .config(
                    "spark.sql.extensions",
                    "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
                )
                # 1. ADDED SNOWFLAKE & UPDATED ICEBERG PACKAGES
                .config(
                    "spark.jars.packages",
                    "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3,"
                    "org.apache.hadoop:hadoop-aws:3.3.4,"
                    "com.amazonaws:aws-java-sdk-bundle:1.12.262,"
                    "net.snowflake:spark-snowflake_2.12:2.15.0-spark_3.5",  # <--- Mandatory for GoldIngestor
                )
                # THE KILLER FIXES FOR SCHEMA MERGE ERRORS
                .config("spark.sql.parquet.mergeSchema", "false")
                .config("spark.sql.files.ignoreCorruptFiles", "true")
                .config("spark.sql.parquet.enableVectorizedReader", "false")
                # ----------------------------------------------
                # GoldIngestor uses 'glue_catalog.silver...', so it must be defined here.
                .config(
                    "spark.sql.catalog.glue_catalog",
                    "org.apache.iceberg.spark.SparkCatalog",
                )
                .config("spark.sql.catalog.glue_catalog.type", "hadoop")
                .config(
                    "spark.sql.catalog.glue_catalog.warehouse",
                    f"s3a://{PROJECT_NAME}-silver/warehouse/",
                )
                .config("spark.hadoop.fs.s3a.endpoint", AWS_ENDPOINT)
                .config("spark.hadoop.fs.s3a.access.key", "test")
                .config("spark.hadoop.fs.s3a.secret.key", "test")
                .config("spark.hadoop.fs.s3a.path.style.access", "true")
                .config(
                    "spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"
                )
            )

            session = builder.getOrCreate()
            session.sparkContext.setLogLevel("ERROR")

            # FIX: Assisting the linter in recognizing the Hadoop Configuration
            # Use the session's internal gateway to avoid the "Unknown" type error
            sc = session.sparkContext
            if sc._jsc:
                hadoop_conf = sc._jsc.hadoopConfiguration()
                hadoop_conf.set("fs.s3a.endpoint", AWS_ENDPOINT)
                hadoop_conf.set("fs.s3a.connection.ssl.enabled", "false")

            log.info("spark_session_created", app_id=session.sparkContext.applicationId)
            return session

        except Exception as e:
            log.error("spark_initialization_failure", error=str(e))
            raise
