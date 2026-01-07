# bronze_ingestion_news_api.py
import boto3
import json
import requests
import sys
import os

import structlog
from utils.logging_config import setup_logging

log = structlog.get_logger()


def get_s3_secrets():
    # Boto3 automatically reads AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY
    # from your environment variables. No need to hardcode them here.
    sm_client = boto3.client(
        "secretsmanager",
        region_name="us-east-1",
        endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
    )

    try:
        response = sm_client.get_secret_value(SecretId="news_api_credentials")
        secrets = json.loads(response["SecretString"])
        return secrets.get("api_key"), "silicon-intel-bronze"
    except Exception:
        log.error("infrastructure_error", exc_info=True)
        sys.exit(1)


def run_ingestion():
    api_key, bucket_name = get_s3_secrets()
    query = "intel AND silicon"
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"

    log.info("starting_ingestion", query=query, target_bucket=bucket_name)

    try:
        response = requests.get(url)
        response.raise_for_status()

        raw_data = response.json()

        s3_client = boto3.client(
            "s3",
            endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
            region_name="us-east-1",
        )

        file_key = "news_data_raw.json"
        s3_client.put_object(
            Bucket=bucket_name, Key=file_key, Body=json.dumps(raw_data, indent=4)
        )

        log.info("ingestion_success", bucket=bucket_name, key=file_key)
        return {"success": True, "file": file_key}

    except requests.exceptions.HTTPError:
        log.error("api_http_error", status_code=response.status_code, exc_info=True)
    except requests.exceptions.JSONDecodeError:
        log.error("json_decode_error", error="API returned invalid JSON", exc_info=True)
    except requests.exceptions.RequestException:
        log.error("network_error", exc_info=True)
    except Exception:
        log.error("unexpected_error", exc_info=True)

    return {"success": False, "error": "Ingestion failed"}


if __name__ == "__main__":
    setup_logging()

    run_ingestion()
