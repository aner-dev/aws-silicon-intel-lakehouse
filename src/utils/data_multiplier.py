import pyspark.sql.functions as F

# IMPORT YOUR CENTRALIZED SESSION FACTORY
from config.spark_setup import SparkSessionFactory


def run_multiplier(input_path: str, output_table: str, iterations: int = 1000):
    # USE THE GLOBALLY CONFIGURED SESSION
    spark = SparkSessionFactory.get_session()

    # 1. Seed ingestion
    raw_df = spark.read.json(input_path)
    base_df = raw_df.select(F.explode("articles").alias("data")).select("data.*")

    # 2. Massive data generation (Logic remains the same)
    multiplier_df = spark.range(0, iterations).withColumnRenamed("id", "idx")
    heavy_df = (
        base_df.crossJoin(multiplier_df)
        .withColumn("article_uuid", F.expr("uuid()"))
        .withColumn("ingestion_timestamp", F.current_timestamp())
        .withColumn("author", F.concat(F.col("author"), F.lit("_"), F.col("idx")))
        .withColumn("source_name", F.col("source.name"))
        .drop("source")
    )

    # 3. Write to Iceberg
    # IMPORTANT: Use the catalog name defined in spark_setup.py
    heavy_df.writeTo(output_table).createOrReplace()
    print(f"--- SUCCESS: {heavy_df.count()} records written to {output_table} ---")


if __name__ == "__main__":
    SAMPLE_PATH = "s3a://silicon-intel-bronze/bronze/news_api/*/*/*/*.json"

    # UPDATE: Must match the catalog name in spark_setup.py
    # If spark_setup uses 'iceberg', use 'iceberg' here
    run_multiplier(SAMPLE_PATH, "iceberg.silver.heavy_news_silver")

