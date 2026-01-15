output "sqs_queue_url" {
  description = "The URL of the SQS queue for processing alerts"
  value       = aws_sqs_queue.spark_alerts_queue.id
}

output "pipeline_alerts_topic_arn" {
  description = "ARN of the pipeline alerts SNS topic"
  value       = aws_sns_topic.pipeline_alerts.arn
}


