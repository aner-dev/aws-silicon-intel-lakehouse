import json
from utils.logging_config import log


def lambda_handler(event, context):
    """
    Consumes structured pipeline metadata from SQS and logs it via structlog.
    """
    log.info(
        "observability_processor_started", records_count=len(event.get("Records", []))
    )

    for record in event.get("Records", []):
        try:
            # 1. SQS Body contains the SNS Envelope
            sns_envelope = json.loads(record["body"])

            # 2. SNS 'Message' contains our actual JSON payload from observability.py
            pipeline_data = json.loads(sns_envelope["Message"])

            job_name = pipeline_data.get("job", "unknown_job")
            status = pipeline_data.get("status", "UNDEFINED")
            error = pipeline_data.get("error")
            timestamp = pipeline_data.get("timestamp")

            # Structured Logging logic
            if status == "FAILED":
                log.error(
                    "pipeline_failure_detected",
                    job=job_name,
                    error=error,
                    job_timestamp=timestamp,
                )
            else:
                log.info(
                    "pipeline_audit_event",
                    job=job_name,
                    status=status,
                    job_timestamp=timestamp,
                )

        except Exception as e:
            log.error(
                "event_parsing_failed", error=str(e), raw_record=record.get("messageId")
            )

    return {"statusCode": 200, "body": "Events processed"}

