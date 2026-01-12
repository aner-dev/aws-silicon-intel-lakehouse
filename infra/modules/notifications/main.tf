resource "aws_sns_topic" "pipeline_alerts" {
  name = "data-pipeline-alerts"
}

resource "aws_sqs_queue" "spark_alerts_queue" {
  name                      = "spark-job-alerts"
  delay_seconds             = 0
  max_message_size          = 262144
  message_retention_seconds = 345600
  receive_wait_time_seconds = 10
}

resource "aws_sns_topic_subscription" "spark_alerts_subscription" {
  topic_arn = aws_sns_topic.pipeline_alerts.arn
  protocol  = "sqs"
  endpoint  = aws_sqs_queue.spark_alerts_queue.arn
}
