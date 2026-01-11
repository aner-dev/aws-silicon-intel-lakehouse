output "sns_topic_arn" {
  description = "The ARN of the SNS topic for alerts"
  value       = aws_sns_topic.pipeline_alerts.arn
}

output "sqs_queue_url" {
  description = "The URL of the SQS queue for processing alerts"
  value       = aws_sqs_queue.spark_alerts_queue.id
}

