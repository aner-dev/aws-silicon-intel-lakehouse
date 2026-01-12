output "bronze_bucket_id" {
  value = aws_s3_bucket.bronze.id
}

output "silver_bucket_id" {
  value = aws_s3_bucket.silver.id
}

output "gold_bucket_id" {
  value = aws_s3_bucket.gold.id
}
