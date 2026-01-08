import sys
from pyspark.sql import SparkSession
import great_expectations as gx


def run_quality_checks():
    spark = SparkSession.builder.appName("SilverQualityChecks").get_session()

    # 1. Load the Silver table (Iceberg)
    # Adjusted to your table name in LocalStack
    df = spark.read.table("demo.silicon_intel.news_silver")

    # 2. Configure GX
    context = gx.get_context()

    # Create an ephemeral datasource for Spark
    datasource_name = "silver_data"
    data_asset_name = "news_articles"

    datasource = context.sources.add_spark(name=datasource_name)
    asset = datasource.add_dataframe_asset(name=data_asset_name)

    # 3. Define the "Expectations" (The rules)
    # Create a Batch Request to validate the current data
    batch_request = asset.build_batch_request(dataframe=df)

    expectation_suite_name = "silver_suite"
    context.add_or_update_expectation_suite(
        expectation_suite_name=expectation_suite_name
    )

    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=expectation_suite_name,
    )

    # --- HERE WE DEFINE THE RULES ---

    # Rule 1: Title cannot be null
    validator.expect_column_values_to_not_be_null(column="title")

    # Rule 2: We must have at least one record (file is not empty)
    validator.expect_table_row_count_to_be_between(min_value=1)

    # Rule 3: The 'source' column must be of type String
    validator.expect_column_values_to_be_of_type(column="source", type_="StringType")

    # 4. Run validation
    checkpoint_result = validator.validate()

    if not checkpoint_result["success"]:
        print("❌ Data Quality Checks FAILED")
        # This causes GitHub Actions to fail if quality is poor
        sys.exit(1)

    print("✅ Data Quality Checks PASSED")


if __name__ == "__main__":
    run_quality_checks()
