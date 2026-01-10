import boto3
from botocore import UNSIGNED
from botocore.config import Config
from utils.logging_config import log


def ingest_amazon_reviews(category="Electronics", limit_gb=10):
    """
    Ingests Amazon Reviews (Parquet) from Public S3 to LocalStack S3.
    """
    # Public AWS Source (No credentials needed for this specific bucket)
    s3_public = boto3.client(
        "s3", config=Config(signature_version=UNSIGNED), region_name="us-east-1"
    )

    # Your LocalStack Destination
    s3_local = boto3.client(
        "s3",
        endpoint_url="http://localhost:4566",
        aws_access_key_id="test",
        aws_secret_access_key="test",
        region_name="us-east-1",
    )

    bucket_public = "amazon-reviews-pds"
    prefix_public = f"parquet/product_category={category}/"
    bucket_local = "silicon-intel-bronze"
    prefix_local = f"bronze/amazon_reviews/{category}/"

    log.info("starting_ingestion", source=bucket_public, category=category)

    try:
        # List objects in the public bucket
        response = s3_public.list_objects_v2(Bucket=bucket_public, Prefix=prefix_public)
        files = response.get("Contents", [])

        total_size_bytes = 0
        max_bytes = limit_gb * 1024 * 1024 * 1024

        for file in files:
            key = file["Key"]
            size = file["Size"]

            if total_size_bytes + size > max_bytes:
                log.info("limit_reached", limit_gb=limit_gb)
                break

            # Stream from Public S3 to LocalStack S3
            log.info("transferring_file", key=key, size_mb=round(size / 1024 / 1024, 2))

            # Get the object from public
            obj = s3_public.get_object(Bucket=bucket_public, Key=key)

            # Upload to LocalStack
            s3_local.put_object(
                Bucket=bucket_local,
                Key=key.replace(prefix_public, prefix_local),
                Body=obj["Body"].read(),
            )

            total_size_bytes += size

        log.info(
            "ingestion_complete",
            total_gb=round(total_size_bytes / 1024 / 1024 / 1024, 2),
        )

    except Exception as e:
        log.error("ingestion_failed", error=str(e))


if __name__ == "__main__":
    ingest_amazon_reviews(limit_gb=5)  # Start with 5GB to test your Artix setup
