from airflow.sdk.timezone import utc
import boto3
import uuid
import json
import os
from datetime import datetime, timedelta
from utils.logging_config import log

# 1. Global Initialization (Faster execution)
AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
AWS_REGION = os.getenv("AWS_DEFAULT_REGION", "us-east-1")
SNS_TOPIC_ARN = os.getenv(
    "SNS_TOPIC_ARN", "arn:aws:sns:us-east-1:000000000000:data-pipeline-alerts"
)
AUDIT_TABLE_NAME = os.getenv("AUDIT_TABLE_NAME", "pipeline_audit")

# REFACTOR: Initialize clients once in GLOBAL/MODULE SCOPE, avoiding Initialize a boto.client in each function call
SNS_CLIENT = boto3.client("sns", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)
DYNAMO_RESOURCE = boto3.resource(
    "dynamodb", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION
)
TABLE = DYNAMO_RESOURCE.Table(AUDIT_TABLE_NAME)
# using resource instead of client for dynamodb because it store data as "TYPED JSON" -> see docs/notes/boto3


def notify_failure(job_name: str, error_message: str):
    """Publishes failure to SNS for fan-out (SQS, Email, etc.)"""
    message_payload = {
        "job": job_name,
        "status": "FAILED",
        "error": error_message,
        "timestamp": datetime.now(tz=utc).isoformat(),  # UTC for global consistency
    }

    try:
        SNS_CLIENT.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message_payload),
            Subject=f"🚨 Pipeline Failure: {job_name}",
        )
        log.info("observability_alert_published", job=job_name)
    except Exception as e:
        # REFACTOR: Log the original error message if the notifier fails
        log.error("observability_alert_failed", error=str(e), original_job=job_name)


def log_job_status(
    job_name: str,
    status: str,
    details: str,
    execution_id: str | None = None,
    metrics: dict | None = None,
):
    """Logs job audit trail to DynamoDB"""
    run_id = execution_id or str(uuid.uuid4())

    # Calculate expiration (e.g., 30 days from now)
    # TTL MUST be in seconds (int)
    expiration_date = datetime.now(tz=utc) + timedelta(days=30)
    ttl_value = int(expiration_date.timestamp())

    item = {
        "job_run_id": f"{job_name}#{run_id}",
        "job_name": job_name,
        "status": status,
        "details": details,
        "metrics": metrics or {},
        "timestamp": datetime.now(tz=utc).isoformat(),  # For humans
        "ttl_timestamp": ttl_value,  # For DynamoDB
    }

    try:
        TABLE.put_item(Item=item)
        log.info("audit_log_updated", job_name=job_name, status=status, run_id=run_id)
    except Exception as e:
        log.error("audit_log_failed", error=str(e))


def enable_table_ttl(table_name):
    SNS_CLIENT.update_time_to_live(
        TableName=table_name,
        TimeToLiveSpecification={"Enabled": True, "AttributeName": "ttl_timestamp"},
    )
    log.info(f"TTL enabled on {table_name} using attribute 'ttl_timestamp'")
