# This file serves as the "Return Value" of the entire infrastructure

# storage output
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

# observability outputs
output "audit_dynamodb_table_name" {
  description = "Audit table for pipeline execution"
  value       = module.database.table_name
}

output "alerts_topic_arn" {
  description = "ARN of the alerts topic used for pipeline notifications"
  value       = module.notifications.alerts_topic_arn
}


# IAM output
output "bronze_role_arn" {
  value       = module.iam_bronze.role_arn
  description = "The ARN of the IAM role for Bronze ingestion"
}

output "silver_role_arn" {
  value       = module.iam_silver.role_arn
  description = "The ARN of the IAM role for Silver processing"
}
