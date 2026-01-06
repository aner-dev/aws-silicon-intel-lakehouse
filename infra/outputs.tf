output "bronze_bucket_name" {
  value = aws_s3_bucket.layers["bronze"].id
}

output "secret_arn" {
  value = aws_secretsmanager_secret.news_api_key.arn
}
