import os
import uuid
import json
import boto3
from datetime import datetime, timedelta
from airflow.sdk.timezone import utc
from utils.logging_config import log


# TODO:: IAM | Needs permission to write to DynamoDB and publish to SNS.
# this Python Class works as a State Ledger
class ObservabilityManager:
    def __init__(self):
        # Config Storage (Stored, but not validated yet)
        self.config = {
            "endpoint": os.getenv("AWS_ENDPOINT_URL", "http://localhost:4566"),
            "region": os.getenv("AWS_DEFAULT_REGION", "us-east-1"),
            "sns_topic": os.getenv("PIPELINE_ALERTS_TOPIC_ARN"),
            "audit_table": os.getenv("AUDIT_TABLE_NAME", "pipeline_audit"),
        }
        self._sns_client = None
        self._dynamo_table = None

    def _validate_config(self, key: str) -> str:
        """Internal helper to validate critical config before use."""
        value = self.config.get(key)
        if not value:
            log.critical(
                f"missing_{key}", message=f"Pipeline cannot function without {key}"
            )
            raise EnvironmentError(f"Missing required environment variable for {key}")
        return str(value)

    @property
    def sns(self):
        if self._sns_client is None:
            self._validate_config("sns_topic")
            log.info("initializing_sns_client")
            self._sns_client = boto3.client(
                "sns",
                endpoint_url=self.config["endpoint"],
                region_name=self.config["region"],
            )
        return self._sns_client

    @property
    def table(self):
        if self._dynamo_table is None:
            table_name = self._validate_config("audit_table")
            log.info("initializing_dynamo_resource")
            resource = boto3.resource(
                "dynamodb",
                endpoint_url=self.config["endpoint"],
                region_name=self.config["region"],
            )
            self._dynamo_table = resource.Table(table_name)
        return self._dynamo_table

    def notify_failure(self, job_name: str, error_message: str):
        payload = {
            "job": job_name,
            "status": "FAILED",
            "error": error_message,
            "timestamp": datetime.now(tz=utc).isoformat(),
        }
        try:
            self.sns.publish(
                TopicArn=self.config["sns_topic"],
                Message=json.dumps(payload),
                Subject=f"🚨 Failure: {job_name}",
            )
            log.info("alert_published", job=job_name)
        except Exception as e:
            log.error("alert_failed", error=str(e), original_job=job_name)

    def log_status(
        self, job_name: str, status: str, details: str, metrics: dict | None = None
    ):
        expiration = datetime.now(tz=utc) + timedelta(days=30)
        item = {
            "job_run_id": f"{job_name}#{uuid.uuid4()}",
            "job_name": job_name,
            "status": status,
            "details": details,
            "metrics": metrics or {},
            "timestamp": datetime.now(tz=utc).isoformat(),
            "ttl_timestamp": int(expiration.timestamp()),
        }
        try:
            self.table.put_item(Item=item)
            log.info("audit_updated", job=job_name, status=status)
        except Exception as e:
            log.error("audit_failed", error=str(e))


obs = ObservabilityManager()
