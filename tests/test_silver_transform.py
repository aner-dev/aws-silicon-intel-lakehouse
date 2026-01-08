import pytest
from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from transform.silver_transform_pyspark_news_api import (
    transform_articles,
    NEWS_SCHEMA,
)


@pytest.fixture(scope="session")
def spark():
    """Fixture to provide a reusable local SparkSession."""
    return (
        SparkSession.builder.master("local[1]")
        .appName("Unit-Testing-Silver")
        .config("spark.sql.shuffle.partitions", "1")
        .getOrCreate()
    )


def test_transform_articles_removes_deleted_content(spark):
    """Tests that articles with the title '[Removed]' are filtered out."""
    # 1. Setup: Create data simulating the API JSON
    input_data = [
        {
            "articles": [
                {
                    "source": {"name": "Valid Tech"},
                    "author": "John Doe",
                    "title": "Intel breaks records",
                    "url": "https://tech.com",
                    "publishedAt": "2026-01-08T10:00:00Z",
                    "content": "Good content",
                },
                {
                    "source": {"name": "N/A"},
                    "author": None,
                    "title": "[Removed]",
                    "url": "https://removed.com",
                    "publishedAt": "2026-01-08T11:00:00Z",
                    "content": None,
                },
            ]
        }
    ]

    # Create the DataFrame using your actual NEWS_SCHEMA
    raw_df = spark.createDataFrame(input_data, NEWS_SCHEMA)

    # 2. Execute: Apply the pure transformation function
    result_df = transform_articles(raw_df)

    # 3. Assert: Only 1 record should remain
    assert result_df.count() == 1
    assert result_df.filter(F.col("title") == "[Removed]").count() == 0
    assert "event_date" in result_df.columns
    assert "processed_at" in result_df.columns


def test_transform_articles_drop_duplicates(spark):
    """Tests that duplicates based on title and date are removed."""
    input_data = [
        {
            "articles": [
                {
                    "source": {"name": "Tech"},
                    "title": "Duplicate News",
                    "publishedAt": "2026-01-08T10:00:00Z",
                    "url": "url1",
                },
                {
                    "source": {"name": "Tech"},
                    "title": "Duplicate News",
                    "publishedAt": "2026-01-08T10:00:00Z",
                    "url": "url2",
                },
            ]
        }
    ]
    raw_df = spark.createDataFrame(input_data, NEWS_SCHEMA)
    result_df = transform_articles(raw_df)

    # Only 1 record should remain despite having 2 in the input
    assert result_df.count() == 1
