from pyspark.sql import SparkSession
from utils.logging_config import log


log.info("spark_session_started", app_id="silicon-intel-01", layer="bronze")


class SparkSessionFactory:
    @staticmethod
    def get_session():
        try:
            log.info("spark_session_request", layer="gold", catalog="hadoop")

            session: SparkSession = (
                SparkSession.builder.appName("SiliconIntelLakehouse")
                .config(
                    "spark.jars.packages",
                    "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3,"
                    "org.apache.hadoop:hadoop-aws:3.3.4",
                )
                # Configuration for use Roles (STS)
                .config(
                    "spark.hadoop.fs.s3a.aws.credentials.provider",
                    "org.apache.hadoop.fs.s3a.auth.AssumedRoleCredentialProvider",  # IAM roles
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
                .config(
                    "spark.sql.catalog.gold", "org.apache.iceberg.spark.SparkCatalog"
                )
                .config("spark.sql.catalog.gold.type", "hadoop")
                .config(
                    "spark.sql.catalog.gold.warehouse",
                    "s3a://silicon-intel-gold/iceberg/",
                )
                .getOrCreate()
            )
            app_id = session.sparkContext.applicationId  # type: ignore

            # Succes log with technical metadata
            log.info(
                "spark_session_created", spark_version=session.version, app_id=app_id
            )
            return session
        except Exception as e:
            # CRITICAL: Log failure detailed
            log.error(
                "spark_session_failed", error=str(e), exc_info=True
            )  # This prints the complete StackTrace
            raise  # Re-raise the error to stop the pipeline (Circuit Breaker)
