provider "aws" {
  region     = "us-east-1"
  access_key = "test"
  secret_key = "test"

  # Estas banderas son vitales para engañar a Terraform y que no busque AWS real
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true # LocalStack usa path-style (s3://bucket/obj)

  endpoints {
    s3    = "http://localhost:4566"
    glue  = "http://localhost:4566"
  }
}
