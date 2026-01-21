# --- BRONZE ---
output "bronze_bucket_id" {
  description = "The name of the Bronze bucket (for Python/Boto3)"
  value       = aws_s3_bucket.this["bronze"].id
}

output "bronze_bucket_arn" {
  description = "The ARN of the Bronze bucket (for IAM Policies)"
  value       = aws_s3_bucket.this["bronze"].arn
}

# --- SILVER ---
output "silver_bucket_id" {
  description = "The name of the Silver bucket"
  value       = aws_s3_bucket.this["silver"].id
}

output "silver_bucket_arn" {
  description = "The ARN of the Silver bucket"
  value       = aws_s3_bucket.this["silver"].arn
}

# --- GOLD ---
output "gold_bucket_id" {
  description = "The name of the Gold bucket"
  value       = aws_s3_bucket.this["gold"].id
}

output "gold_bucket_arn" {
  description = "The ARN of the Gold bucket"
  value       = aws_s3_bucket.this["gold"].arn
}
