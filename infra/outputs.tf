#--- Updated S3 Outputs (Fixed to match the new module names) ---
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

output "dynamodb_table_name" {
  description = "Audit table for pipeline execution"
  value       = module.database.table_name
}

output "alerts_topic_arn" {
  value = module.notifications.sns_topic_arn
}
