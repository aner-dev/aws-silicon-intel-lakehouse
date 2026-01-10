# bronze_ingestion_news_api.py
import boto3
import json
import requests
import sys
import os
from datetime import datetime
from utils.logging_config import log, setup_logging


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


def log_audit_dynamo(file_key, status):
    """GAP: Currently, the pipeline is not able to show which files failed without checking logs.
    Dynamo solves this."""
    dynamo = boto3.resource(
        "dynamodb", endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    )
    table = dynamo.Table("pipeline_audit")
    table.put_item(
        Item={
            "job_id": f"news_api_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "file_key": file_key,
            "status": status,
            "timestamp": datetime.now().isoformat(),
            "layer": "bronze",  # added layer for posterior filtering in DynamoDB
        }
    )


def send_sns_alert(error_message):
    """GAP: If the script fails in the middle of the night, no one finds out."""
    sns = boto3.client(
        "sns", endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
    )

    # El nombre debe coincidir EXACTAMENTE con el de notifications.tf
    topic_name = "data-pipeline-alerts"
    topic_arn = f"arn:aws:sns:us-east-1:000000000000:{topic_name}"

    try:
        sns.publish(
            TopicArn=topic_arn,
            Message=f"CRITICAL: Bronze Ingestion Failed: {error_message}",
            Subject="Pipeline Alert: Bronze Layer",
        )
    except Exception as e:
        log.error("sns_alert_failed", error=str(e))


def run_ingestion(topic="intel_silicon"):
    api_key, bucket_name = get_s3_secrets()
    query = topic.replace("_", " AND ")
    url = f"https://newsapi.org/v2/everything?q={query}&apiKey={api_key}"
    full_key = "N/A"  # Placeholder for log in case of early error

    try:
        # 1. API REQUEST
        log.info("starting_api_request", query=query)
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        raw_data = response.json()

        # 2. S3 PREPARATION
        now = datetime.now()
        # Matches the 'ingested_at' column name used in Silver (pypsark processing)
        partition_path = f"topic={topic}/ingested_at={now.strftime('%Y-%m-%d')}"
        file_name = f"news_{now.strftime('%H%M%S')}.json"
        full_key = f"bronze/news_api/{partition_path}/{file_name}"

        s3_client = boto3.client(
            "s3",
            endpoint_url=os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
        )

        # 3. S3 UPLOAD (Capture red/permissions failures)
        log.info("uploading_to_s3", bucket=bucket_name, key=full_key)
        s3_client.put_object(
            Bucket=bucket_name, Key=full_key, Body=json.dumps(raw_data)
        )

        # 4. AUDIT LOG (DynamoDB)
        log_audit_dynamo(full_key, "SUCCESS")

        log.info("ingestion_success", key=full_key)
        return {"success": True, "file": full_key}

    except requests.exceptions.RequestException as e:
        # API specific errors
        error_msg = f"API_ERROR: {str(e)}"
        log.error("api_failed", error=error_msg)
        send_sns_alert(error_msg)
        log_audit_dynamo(full_key, "FAILED_API")
        raise

    except Exception as e:
        # Capture failures of S3, Dynamo or unexpected errors
        error_msg = f"INFRASTRUCTURE_ERROR: {str(e)}"
        log.error("ingestion_failed", error=error_msg, exc_info=True)
        send_sns_alert(error_msg)
        log_audit_dynamo(full_key, "FAILED_INFRA")
        raise


def lambda_handler(event, context):
    setup_logging()  # Ensure logs work in CloudWatch
    topic = event.get("topic", "intel_silicon")
    try:
        result = run_ingestion(topic)
        return {"statusCode": 200, "body": json.dumps(result)}
    except Exception as e:
        return {"statusCode": 500, "body": json.dumps({"error": str(e)})}


# 3. The Local Entry Point (Replacing main)
if __name__ == "__main__":
    setup_logging()
    # For local testing, we simulate an 'event'
    test_event = {"topic": "intel_silicon"}
    lambda_handler(test_event, None)
