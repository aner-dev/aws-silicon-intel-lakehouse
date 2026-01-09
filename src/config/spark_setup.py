# spark_setup.py

import os
from pyspark.sql import SparkSession
from pyspark import SparkContext
from utils.logging_config import log

# JUSTIFICATION: Use 'localstack' inside Docker network, 'localhost' for local terminal
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
                .config(
                    "spark.sql.catalog.iceberg", "org.apache.iceberg.spark.SparkCatalog"
                )
                .config("spark.sql.catalog.iceberg.type", "hadoop")
                .config(
                    "spark.sql.catalog.iceberg.warehouse",
                    "s3a://silicon-intel-silver/warehouse/",
                )
                # OPTIMIZATION: 10GB+ logic
                .config("spark.sql.shuffle.partitions", "2")
                .config("spark.sql.iceberg.vectorization.enabled", "true")
                .config(
                    "spark.jars.packages",
                    "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3,"
                    "org.apache.hadoop:hadoop-aws:3.3.4,"
                    "com.amazonaws:aws-java-sdk-bundle:1.12.262",
                )
                # --- S3A SECURITY ---
                .config("spark.hadoop.fs.s3a.endpoint", AWS_ENDPOINT)
                .config("spark.hadoop.fs.s3a.access.key", "test")
                .config("spark.hadoop.fs.s3a.secret.key", "test")
                .config("spark.hadoop.fs.s3a.path.style.access", "true")
                .config("spark.hadoop.fs.s3a.connection.ssl.enabled", "false")
                .config(
                    "spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"
                )
                # DO NOT USE '60s' OR '1m'. Only milliseconds as pure String.
                .config("spark.hadoop.fs.s3a.connection.timeout", "60000")
                .config("spark.hadoop.fs.s3a.connection.establish.timeout", "60000")
                .config("spark.hadoop.fs.s3a.paging.maximum", "5000")
                .config("spark.hadoop.fs.s3a.threads.keepalivetime", "60")
            )

            session = builder.getOrCreate()

            # --- RECOVERING YOUR CONTROL LOGIC ---
            session.sparkContext.setLogLevel("ERROR")
            sc: SparkContext = session.sparkContext

            # JAVA GATEWAY ACCESS: Double validation for the Hadoop environment
            # This fixes the gap where the Spark driver has the config but executors do not.
            hadoop_conf = sc._jsc.hadoopConfiguration()  # type: ignore
            hadoop_conf.set("fs.s3a.connection.timeout", "60000")
            hadoop_conf.set("fs.s3a.connection.establish.timeout", "60000")
            hadoop_conf.set("fs.s3a.experimental.fadvise", "random")
            hadoop_conf.set("fs.s3a.endpoint", AWS_ENDPOINT)
            hadoop_conf.set("fs.s3a.connection.ssl.enabled", "false")

            log.info(
                "spark_session_created",
                app_id=sc.applicationId,
                spark_version=session.version,
            )

            return session

        except ImportError as ie:
            # Specific Error if the JARs or python packages aren't present
            log.error("spark_dependencies_missing", error=str(ie))
            raise

        except Exception as e:
            # Capture network errors (LocalStack) or JVM errors (Spark)
            log.error(
                "spark_initialization_critical_failure",
                error_type=type(e).__name__,
                error=str(e),
                exc_info=True,
            )
            raise
