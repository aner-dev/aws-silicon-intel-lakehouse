import sys
from pyspark.sql import SparkSession
import great_expectations as gx


def run_quality_checks():
    spark = SparkSession.builder.appName("SilverQualityChecks").getOrCreate()

    # 1. Load the Silver table (Iceberg)
    # Adjusted to your table name in LocalStack
    df = spark.read.table("local.silver.news_articles")
    print(f"DEBUG: Silver row count = {df.count()}")

    # 2. Configure GX
    context = gx.get_context()

    # Create an ephemeral datasource for Spark
    datasource_name = "silver_data_source"
    try:
        datasource = context.data_sources.get(datasource_name)
    except Exception:
        datasource = context.data_sources.add_spark(name=datasource_name)

    data_asset_name = "news_articles_asset"
    # Añadimos el asset de Spark
    try:
        asset = datasource.get_asset(data_asset_name)
    except Exception:
        asset = datasource.add_dataframe_asset(name=data_asset_name)

    # 3. Define the "Expectations"
    batch_request = asset.build_batch_request(dataframe=df)

    expectation_suite_name = "silver_suite"
    # CORRECCIÓN 3: Método compatible para añadir suites
    context.suites.add(gx.ExpectationSuite(name=expectation_suite_name))

    validator = context.get_validator(
        batch_request=batch_request,
        expectation_suite_name=expectation_suite_name,
    )

    # --- RULES ---
    validator.expect_column_values_to_not_be_null(column="title")
    validator.expect_table_row_count_to_be_between(min_value=1)

    # Nota: Spark maneja tipos internos, a veces es mejor validar contenido
    validator.expect_column_values_to_be_of_type(column="source", type_="StringType")

    # 4. Run validation
    validation_result = validator.validate()

    if not validation_result["success"]:
        print("❌ Data Quality Checks FAILED")
        # Imprime los resultados fallidos para debuggear en los logs de GitHub
        print(validation_result)
        sys.exit(1)

    print("✅ Data Quality Checks PASSED")


if __name__ == "__main__":
    run_quality_checks()
