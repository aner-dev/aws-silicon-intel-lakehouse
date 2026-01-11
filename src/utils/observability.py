import boto3
import json
import os
from utils.logging_config import log

# Config for LocalStack
AWS_ENDPOINT = os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566")


def notify_failure(job_name: str, error_message: str):
    """Sends a failure alert to SQS for observability."""
    try:
        sqs = boto3.client("sqs", endpoint_url=AWS_ENDPOINT, region_name="us-east-1")

        # We assume the queue 'spark-job-alerts' was created by your Terraform
        queue_url = sqs.get_queue_url(QueueName="spark-job-alerts")["QueueUrl"]

        message_body = {
            "job": job_name,
            "status": "FAILED",
            "error": error_message,
            "timestamp": boto3.client("sns").get_topic_attributes(
                TopicArn="..."
            ),  # Placeholder for metadata
        }

        sqs.send_message(QueueUrl=queue_url, MessageBody=json.dumps(message_body))
        log.info("observability_alert_sent", job=job_name)

    except Exception as e:
        log.error("observability_alert_failed", error=str(e))
