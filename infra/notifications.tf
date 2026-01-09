# Topic for error alerts
resource "aws_sns_topic" "pipeline_alerts" {
  name = "data-pipeline-alerts"
}

# Queue to trigger ingestions (SQS)
resource "aws_sqs_queue" "ingestion_queue" {
  name                      = "news-ingestion-queue"
  receive_wait_time_seconds = 10
}

# Subscribe SQS to SNS so that errors are also queued
resource "aws_sns_topic_subscription" "alerts_to_sqs" {
  topic_arn = aws_sns_topic.pipeline_alerts.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.ingestion_queue.arn
}
