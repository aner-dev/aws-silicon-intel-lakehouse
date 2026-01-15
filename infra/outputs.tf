# This file serves as the "Return Value" of the entire infrastructure
output "bronze_bucket_name" {
  description = "The name of the S3 bucket for Bronze layer"
  value       = module.storage.bronze_bucket_id
}

output "silver_bucket_name" {
  description = "The name of the S3 bucket for Silver (Iceberg) layer"
  value       = module.storage.silver_bucket_id
}

output "gold_bucket_name" {
  description = "The name of the S3 bucket for Gold layer"
  value       = module.storage.gold_bucket_id
}

output "audit_dynamodb_table_name" {
  description = "Audit table for pipeline execution"
  value       = module.database.table_name
}

output "alerts_topic_arn" {
  description = "ARN of the alerts topic used for pipeline notifications"
  value       = module.notifications.pipeline_alerts_topic_arn
}
