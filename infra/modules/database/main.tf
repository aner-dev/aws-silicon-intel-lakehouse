# 1. THE AUDIT LEDGER (Matches observability.py)
resource "aws_dynamodb_table" "audit" {
  name         = var.audit_table_name
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_run_id"

  attribute {
    name = "job_run_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl_timestamp"
    enabled        = true
  }

  tags = var.tags
}

# 2. THE ICEBERG CATALOG
resource "aws_dynamodb_table" "iceberg_catalog" {
  name         = "${var.project_name}-iceberg-catalog"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "identifier"

  attribute {
    name = "identifier"
    type = "S"
  }
}

# 3. SECRETS (Using a variable instead of a local)
resource "aws_secretsmanager_secret" "db_password" {
  name = "${var.secret_prefix}/database/master_password"
}
