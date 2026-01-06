# 1. Secret container
resource "aws_secretsmanager_secret" "news_api_key" {
  name        = "news_api_credentials"
  description = "Credentials for News API ingestion"
}

# 2. Secret value (in JSON format)
resource "aws_secretsmanager_secret_version" "key_val" {
  secret_id = aws_secretsmanager_secret.news_api_key.id
  secret_string = jsonencode({
    api_key = var.news_api_key
  })
}
