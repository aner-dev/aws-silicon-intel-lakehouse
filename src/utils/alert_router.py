import json
from utils.logging_config import log


def lambda_handler(event, context):
    records = event.get("Records", [])
    # Contextual binding for the start of the batch
    logger = log.bind(batch_size=len(records))
    logger.info("observability_processor_triggered")

    for record in records:
        try:
            sns_envelope = json.loads(record["body"])
            payload = json.loads(sns_envelope["Message"])

            # Bind the Execution ID to all logs for this specific record
            # This ensures every log line from here on includes these IDs automatically
            it_logger = logger.bind(
                execution_id=payload.get("execution_id"),
                job_name=payload.get("job"),
                status=payload.get("status"),
            )

            if payload.get("status") == "FAILED":
                it_logger.error(
                    "pipeline_failure_detected",
                    error_message=payload.get("error"),
                    timestamp=payload.get("timestamp"),
                )
                # Here is where would trigger a Slack/PagerDuty notification
            else:
                it_logger.info("pipeline_milestone_reached")

        except Exception as e:
            logger.error("payload_decoding_failed", error=str(e))

    return {"statusCode": 200, "body": "Audit processed"}

