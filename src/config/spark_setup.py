import os
from pyspark.sql import SparkSession

# Removed SparkContext import to fix F401 (imported but unused)
from utils.logging_config import log

AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")


class SparkSessionFactory:
    @staticmethod
    def get_session():
        try:
            log.info(
                "spark_session_request", catalog="iceberg_hadoop", endpoint=AWS_ENDPOINT
            )

            builder = (
                SparkSession.builder.appName("SiliconIntelLakehouse")
                .config(
                    "spark.sql.extensions",
                    "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
                )
                # THE KILLER FIXES FOR SCHEMA MERGE ERRORS
                .config("spark.sql.parquet.mergeSchema", "false")
                .config("spark.sql.files.ignoreCorruptFiles", "true")
                .config("spark.sql.parquet.enableVectorizedReader", "false")
                # ----------------------------------------------
                .config(
                    "spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog"
                )
                .config("spark.sql.catalog.iceberg.type", "hadoop")
                .config(
                    "spark.sql.catalog.iceberg.warehouse",
                    "s3a://silicon-intel-silver/warehouse/",
                )
                .config(
                    "spark.jars.packages",
                    "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3,"
                    "org.apache.hadoop:hadoop-aws:3.3.4,"
                    "com.amazonaws:aws-java-sdk-bundle:1.12.262",
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

            # FIX: Helping the linter recognize the Hadoop Configuration
            # We use the session's internal gateway to avoid the "Unknown" type error
            sc = session.sparkContext
            if sc._jsc:  # type: ignore
                hadoop_conf = sc._jsc.hadoopConfiguration()
                hadoop_conf.set("fs.s3a.endpoint", AWS_ENDPOINT)
                hadoop_conf.set("fs.s3a.connection.ssl.enabled", "false")

            log.info("spark_session_created", app_id=session.sparkContext.applicationId)
            return session

        except Exception as e:
            log.error("spark_initialization_failure", error=str(e))
            raise
