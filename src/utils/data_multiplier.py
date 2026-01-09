from pyspark.sql import SparkSession
import pyspark.sql.functions as F


def get_spark():
    """Spark configuration for Iceberg and LocalStack."""
    return (
        SparkSession.builder.appName("IcebergDataMultiplier")
        .config(
            "spark.sql.extensions",
            "org.apache.iceberg.spark.extensions.IcebergSparkExtensions",
        )
        .config("spark.sql.catalog.local", "org.apache.iceberg.spark.SparkCatalog")
        .config("spark.sql.catalog.local.type", "hadoop")
        .config(
            "spark.sql.catalog.local.warehouse", "s3a://silicon-intel-bronze/warehouse"
        )
        .config("spark.hadoop.fs.s3a.endpoint", "http://localhost:4566")
        .config("spark.hadoop.fs.s3a.path.style.access", "true")
        .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
        .config(
            "spark.jars.packages",
            "org.apache.iceberg:iceberg-spark-runtime-3.5_2.12:1.5.0,org.apache.hadoop:hadoop-aws:3.3.4",
        )
        .getOrCreate()
    )  # <--- CORRECTION HERE


def run_multiplier(input_path: str, output_table: str, iterations: int = 1000):
    spark = get_spark()

    # 1. Seed ingestion
    raw_df = spark.read.json(input_path)
    # Flatten the NewsAPI structure
    base_df = raw_df.select(F.explode("articles").alias("data")).select("data.*")

    # 2. Massive generation
    multiplier_df = spark.range(0, iterations).withColumnRenamed("id", "idx")

    # The crossJoin will multiply your records exponentially
    heavy_df = (
        base_df.crossJoin(multiplier_df)
        .withColumn("article_uuid", F.expr("uuid()"))
        .withColumn("ingestion_timestamp", F.current_timestamp())
        .withColumn("author", F.concat(F.col("author"), F.lit("_"), F.col("idx")))
        .withColumn("source_name", F.col("source.name"))
        .drop("source")
    )

    # 3. Write to Iceberg
    # createOrReplace to ensure the table exists on your first run
    heavy_df.writeTo(output_table).createOrReplace()
    print(f"--- SUCCESS: {heavy_df.count()} records written to {output_table} ---")


if __name__ == "__main__":
    # Simulated local path in LocalStack
    SAMPLE_PATH = (
        "s3a://silicon-intel-bronze/bronze/news_api/year=*/month=*/day=*/*.json"
    )
    run_multiplier(SAMPLE_PATH, "local.db.heavy_news_silver")
