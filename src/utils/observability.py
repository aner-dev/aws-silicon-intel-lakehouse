import boto3
import json
import os
from datetime import datetime
from utils.logging_config import log

# Unified LocalStack Config
AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")
AWS_REGION = "us-east-1"
# This ARN comes from your Terraform outputs
SNS_TOPIC_ARN = "arn:aws:sns:us-east-1:000000000000:data-pipeline-alerts"


def notify_failure(job_name: str, error_message: str):
    """
    Publishes a failure event to SNS.
    The SNS Topic then automatically 'fans out' the message to your SQS queue.
    """
    try:
        sns = boto3.client("sns", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION)

        message_payload = {
            "job": job_name,
            "status": "FAILED",
            "error": error_message,
            "timestamp": datetime.now().isoformat(),
        }

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Message=json.dumps(message_payload),
            Subject=f"🚨 Pipeline Failure: {job_name}",
        )

        log.info("observability_alert_published", job=job_name)

    except Exception as e:
        log.error("observability_alert_failed", error=str(e))


def log_job_status(job_id: str, status: str, details: str):
    """
    Logs the final status of a job to the DynamoDB audit table.
    """
    try:
        dynamo = boto3.resource(
            "dynamodb", endpoint_url=AWS_ENDPOINT, region_name=AWS_REGION
        )
        table = dynamo.Table("pipeline_audit")

        table.put_item(
            Item={
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "status": status,
                "details": details,
            }
        )
        log.info("audit_log_updated", job_id=job_id, status=status)
    except Exception as e:
        log.error("audit_log_failed", error=str(e))
