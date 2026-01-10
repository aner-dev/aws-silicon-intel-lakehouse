output "bronze_bucket_name" {
  description = "The name of the S3 bucket for Bronze layer"
  value       = aws_s3_bucket.layers["bronze"].id
}

output "silver_bucket_name" {
  description = "The name of the S3 bucket for Silver (Iceberg) layer"
  value       = aws_s3_bucket.layers["silver"].id
}

output "gold_bucket_name" {
  description = "The name of the S3 bucket for Gold layer"
  value       = aws_s3_bucket.layers["gold"].id
}

output "secret_arn" {
  description = "The ARN of the News API secret"
  value       = aws_secretsmanager_secret.news_api_key.arn
}

output "dynamodb_table_name" {
  description = "Audit table for pipeline execution"
  value       = aws_dynamodb_table.pipeline_audit.name
}
