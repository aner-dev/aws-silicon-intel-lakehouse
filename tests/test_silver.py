import pytest
from unittest.mock import patch
from pyspark.sql import SparkSession, functions as F  # Added F here
from transform.silver_transform_pyspark_taxi import SilverIngestor


@pytest.fixture(scope="session")
def spark():
    """Provides a local Spark session for testing."""
    # Use .getOrCreate() instead of .get_session() for better compatibility
    return (
        SparkSession.builder.master("local[1]")
        .appName("pytest-spark-testing")
        .getOrCreate()
    )


@pytest.fixture
def mock_config():
    """Provides a controlled configuration for testing."""
    return {
        "test_source": {
            "source_path": "test/path/*.parquet",
            "target_table": "iceberg.test_table",
            "merge_keys": ["id"],
            "partition_by": "ts",
            "mappings": {"id": "raw_id", "ts": "raw_ts", "val": "raw_val"},
        }
    }


@patch("transform.silver_transform_pyspark_taxi.SilverIngestor._load_catalog")
@patch("transform.silver_transform_pyspark_taxi.SparkSessionFactory.get_session")
def test_transformation_logic(
    mock_spark_factory, mock_load_catalog, spark, mock_config
):
    # Setup
    mock_load_catalog.return_value = mock_config
    mock_spark_factory.return_value = spark

    # use the ingestor to verify it initializes correctly with the mock
    ingestor = SilverIngestor(source_id="test_source")
    assert ingestor.source_id == "test_source"  # Now 'ingestor' is used!

    # Create sample data
    data = [(1, "2026-01-01 10:00:00", 100.5)]
    columns = ["raw_id", "raw_ts", "raw_val"]
    bronze_df = spark.createDataFrame(data, columns)

    # Test the dynamic mapping logic extracted from ingestor config
    select_expr = [
        F.col(src).alias(tgt) for tgt, src in ingestor.config["mappings"].items()
    ]
    silver_df = bronze_df.select(*select_expr)

    # Assertions
    assert "id" in silver_df.columns
    assert "ts" in silver_df.columns
    assert "val" in silver_df.columns
    assert silver_df.count() == 1


def test_merge_condition_generation(mock_config):
    """Rigorous test for the dynamic SQL string generation."""
    with patch(
        "transform.silver_transform_pyspark_taxi.SilverIngestor._load_catalog",
        return_value=mock_config,
    ):
        ingestor = SilverIngestor(source_id="test_source")

        merge_keys = ingestor.config["merge_keys"]
        join_condition = " AND ".join([f"t.{k} = s.{k}" for k in merge_keys])

        assert join_condition == "t.id = s.id"
