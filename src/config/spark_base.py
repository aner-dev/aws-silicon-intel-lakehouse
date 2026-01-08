from pyspark.sql import SparkSession
from pyspark import SparkContext
from utils.logging_config import log

LOCALSTACK_ENDPOINT = "http://127.0.0.1:4566"


class SparkSessionFactory:
    @staticmethod
    def get_session():
        try:
            log.info("spark_session_request", catalog="iceberg_hadoop")

            session: SparkSession = (
                SparkSession.builder.appName("SiliconIntelLakehouse")
                .config(
                    "spark.sql.extensions",
                    "org.apache.iceberg.spark.extensions.IcebergSparkSessionExtensions",
                )
                .config(
                    "spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog"
                )
                .config("spark.sql.catalog.local.type", "hadoop")
                .config(
                    "spark.sql.catalog.local.warehouse",
                    "s3a://silicon-intel-gold/iceberg/",
                )
                .config(
                    "spark.jars.packages",
                    "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.4.3,"
                    "org.apache.hadoop:hadoop-aws:3.3.4,"
                    "com.amazonaws:aws-java-sdk-bundle:1.12.262",
                )
                .config(
                    "spark.hadoop.fs.s3a.aws.credentials.provider",
                    "org.apache.hadoop.fs.s3a.SimpleAWSCredentialsProvider",
                )
                .config("spark.hadoop.fs.s3a.endpoint", LOCALSTACK_ENDPOINT)
                .config(
                    "spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"
                )
                .config("spark.hadoop.fs.s3a.access.key", "test")
                .config("spark.hadoop.fs.s3a.secret.key", "test")
                .config("spark.hadoop.fs.s3a.path.style.access", "true")
                # Forzamos los timeouts desde la creación
                .config("spark.hadoop.fs.s3a.connection.timeout", "60000")
                .config("spark.hadoop.fs.s3a.connection.establish.timeout", "60000")
                .config("spark.hadoop.fs.s3a.paging.maximum", "5000")
                .config("spark.hadoop.fs.s3a.threads.keepalivetime", "60")  #
                .getOrCreate()
            )
            # Dentro de get_session, después de crear la sesión:
            session.sparkContext.setLogLevel("ERROR")  # type: ignore

            # Extraemos los atributos de forma segura para el linter
            sc: SparkContext = session.sparkContext  # type: ignore
            app_id = sc.applicationId

            # El acceso a _jsc es necesario para el fix de Hadoop,
            # pero le añadimos un comentario para que el linter lo ignore
            # type: ignore (Esto silencia el warning de 'Unknown object')
            hadoop_conf = sc._jsc.hadoopConfiguration()  # type: ignore
            hadoop_conf.set("fs.s3a.connection.timeout", "60000")  # type: ignore
            hadoop_conf.set("fs.s3a.connection.establish.timeout", "60000")

            log.info(
                "spark_session_created", app_id=app_id, spark_version=session.version
            )

            return session

        except Exception as e:
            log.error("spark_session_failed", error=str(e), exc_info=True)
            raise
