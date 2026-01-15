import json
import boto3
import pytest
from utils.alert_router import lambda_handler
from utils.observability import log_job_status

# --- CONFIGURATION ---
DYNAMO_TABLE = "pipeline_audit"
SQS_URL = "http://localhost:4566/000000000000/observability-queue"  # LocalStack default account


@pytest.fixture
def audit_metadata():
    """Standardized metadata fixture for all observability tests."""
    return {
        "job_id": "integration-test-001",
        "status": "FAILED",
        "message": "Simulated Spark Failure",
        "execution_id": "exec-uuid-999",
    }


def test_producer_dynamodb_write(audit_metadata):
    """
    Validates the 'Producer' side:
    Ensures the observability utility correctly persists state to DynamoDB.
    """
    # 1. Execute the Producer logic
    log_job_status(
        audit_metadata["job_id"], audit_metadata["status"], audit_metadata["message"]
    )

    # 2. Verify in LocalStack DynamoDB
    dynamo = boto3.resource(
        "dynamodb", endpoint_url="http://localhost:4566", region_name="us-east-1"
    )
    table = dynamo.Table(DYNAMO_TABLE)
    response = table.get_item(Key={"job_id": audit_metadata["job_id"]})

    assert "Item" in response, "Audit record was not found in DynamoDB"
    assert response["Item"]["status"] == audit_metadata["status"]


def test_consumer_lambda_logic(audit_metadata, caplog):
    """
    Validates the 'Consumer' side:
    Ensures the Lambda processes the SQS/SNS envelope and binds the Execution ID.
    """
    # 1. Mock the SQS Envelope (The data contract)
    mock_sqs_event = {
        "Records": [
            {
                "body": json.dumps(
                    {
                        "Type": "Notification",
                        "Message": json.dumps(
                            {
                                "job": audit_metadata["job_id"],
                                "status": audit_metadata["status"],
                                "execution_id": audit_metadata["execution_id"],
                                "error": audit_metadata["message"],
                                "timestamp": "2026-01-13T00:00:00",
                            }
                        ),
                    }
                )
            }
        ]
    }

    # 2. Trigger the Lambda handler
    lambda_handler(mock_sqs_event, None)

    # 3. Assert Context-Aware Logging (The Correlation ID check)
    assert audit_metadata["execution_id"] in caplog.text
    assert "pipeline_failure_detected" in caplog.text
