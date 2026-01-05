# terraform/main.tf
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true

  endpoints {
    s3             = "http://localhost:4566"
    iam            = "http://localhost:4566"
    secretsmanager = "http://localhost:4566"
  }
}

resource "aws_s3_bucket" "layers" {
  for_each = toset(["bronze", "silver", "gold"])
  bucket   = "silicon-intel-${each.value}"
}

# terraform/secrets.tf
resource "aws_secretsmanager_secret" "news_api_key" {
  name = "news_api_credentials"
}

resource "aws_secretsmanager_secret_version" "key_val" {
  secret_id     = aws_secretsmanager_secret.news_api_key.id
  secret_string = jsonencode({ api_key = "TU_NEWS_API_KEY_AQUI" })
}
