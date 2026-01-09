resource "aws_dynamodb_table" "pipeline_audit" {
  name           = "pipeline_audit"
  billing_mode   = "PAY_PER_REQUEST"
  hash_key       = "job_id"

  attribute {
    name = "job_id"
    type = "S"
  }

  tags = {
    Project = "SiliconIntel"
  }
}
