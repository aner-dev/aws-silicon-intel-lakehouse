resource "aws_dynamodb_table" "pipeline_audit" {
  name         = "pipeline_audit"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_id"

  attribute {
    name = "job_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl_timestamp"
    enabled        = true
  }

  tags = {
    # Refactor: Use the variable here instead of a hardcoded string
    Project = "var.project_name"
  }
}
# Use DynamoDB as the Iceberg Catalog Ref 
resource "aws_dynamodb_table" "iceberg_catalog" {
  name         = "iceberg_catalog"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "identifier"

  attribute {
    name = "identifier"
    type = "S"
  }
}
