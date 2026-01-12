resource "aws_dynamodb_table" "pipeline_audit" {
  name         = "pipeline_audit"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "job_id"

  attribute {
    name = "job_id"
    type = "S"
  }

  tags = {
    # Refactor: Use the variable here instead of a hardcoded string
    Project = "var.project_name"
  }
}
resource "aws_glue_catalog_database" "silver_db" {
  name = "silver" # Keeping this simple makes the Spark catalog 'glue_catalog.silver' work
}
