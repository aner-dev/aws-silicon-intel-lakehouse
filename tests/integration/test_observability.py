import boto3
import pytest
from utils.observability import log_job_status


def test_dynamodb_logging():
    # Execute
    log_job_status("pytest-001", "TEST_RUN", "Testing logic")

    # Verify
    dynamo = boto3.resource(
        "dynamodb", endpoint_url="http://localhost:4566", region_name="us-east-1"
    )
    table = dynamo.Table("pipeline_audit")
    response = table.get_item(Key={"job_id": "pytest-001"})

    assert response["Item"]["status"] == "TEST_RUN"
