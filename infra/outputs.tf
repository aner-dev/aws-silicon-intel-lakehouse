output "bronze_bucket_name" {
  description = "The name of the S3 bucket for Bronze layer"
  value       = module.storage.bucket_ids["bronze"]
}

output "silver_bucket_name" {
  description = "The name of the S3 bucket for Silver (Iceberg) layer"
  value       = module.storage.bucket_ids["silver"]
}

output "gold_bucket_name" {
  description = "The name of the S3 bucket for Gold layer"
  value       = module.storage.bucket_ids["gold"]
}

output "dynamodb_table_name" {
  description = "Audit table for pipeline execution"
  value       = module.database.table_name
}

output "alerts_topic_arn" {
  value = module.notifications.sns_topic_arn
}
