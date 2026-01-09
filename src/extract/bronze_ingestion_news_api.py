# bronze_ingestion_news_api.py
import boto3
import json
import requests
import sys
import os
from datetime import datetime
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
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        raw_data = response.json()

    except requests.exceptions.HTTPError as errh:
        log.error("api_http_error", status=response.status_code, error=str(errh))
        raise SystemExit(errh)  # Stops the pipeline
    except requests.exceptions.ConnectionError as errc:
        log.error("api_connection_error", error=str(errc))
        raise SystemExit(errc)
    except requests.exceptions.Timeout as errt:
        log.error("api_timeout_error", error=str(errt))
        raise SystemExit(errt)
    except requests.exceptions.JSONDecodeError as errj:
        log.info("api_malformed_json", error=str(errj))
        raise SystemExit(errj)
    except Exception as e:
        log.error("unidentified_error", error=str(e))
        raise e

    s3_client = boto3.client(
        "s3",
        endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
        region_name="us-east-1",
    )
    now = datetime.now()
    partition_path = f"year={now.year}/month={now.month:02d}/day={now.day:02d}"
    file_name = f"news_{now.strftime('%H%M%S')}.json"
    full_key = f"bronze/news_api/{partition_path}/{file_name}"

    s3_client.put_object(Bucket=bucket_name, Key=full_key, Body=json.dumps(raw_data))

    log.info("ingestion_success", bucket=bucket_name, key=full_key)
    return {"success": True, "file": full_key}


if __name__ == "__main__":
    setup_logging()

    run_ingestion()
