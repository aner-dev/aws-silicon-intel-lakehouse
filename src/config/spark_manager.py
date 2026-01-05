from pyspark.sql import SparkSession
from src.logging_config import log

log.info("spark_session_started", app_id="silicon-intel-01", layer="bronze")


class SparkSessionFactory:
    @staticmethod
    def get_session():
        return (
            SparkSession.builder.appName("SiliconIntelLakehouse")
            .config(
                "spark.jars.packages",
                "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3,"
                "org.apache.hadoop:hadoop-aws:3.3.4",
            )
            # Configuration for use Roles (STS)
            .config(
                "spark.hadoop.fs.s3a.aws.credentials.provider",
                "org.apache.hadoop.fs.s3a.auth.AssumedRoleCredentialProvider",
            )
            .config(
                "spark.hadoop.fs.s3a.assumed.role.arn",
                "arn:aws:iam::000000000000:role/SparkDataProcessorRole",
            )
            .config(
                "spark.hadoop.fs.s3a.assumed.role.sts.endpoint",
                "http://localstack:4566",
            )
            .config("spark.hadoop.fs.s3a.endpoint", "http://localstack:4566")
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            # Iceberg Hadoop Catalog (Free & Reliable)
            .config("spark.sql.catalog.gold", "org.apache.iceberg.spark.SparkCatalog")
            .config("spark.sql.catalog.gold.type", "hadoop")
            .config(
                "spark.sql.catalog.gold.warehouse", "s3a://silicon-intel-gold/iceberg/"
            )
            .getOrCreate()
        )
