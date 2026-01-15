terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    postgresql = {
      source  = ""
      version = "~> 14.0"
    }
  }

  required_version = ">= 1.2.0"

  backend "s3" {
    bucket = "terraform-state-bucket"  # Where the file lives
    key    = "state/terraform.tfstate" # Path inside the bucket
    region = "us-east-1"

    # LOCKING MECHANISM
    dynamodb_table = "terraform-state-lock" # the "Mutex"
    encrypt        = true

    # LOCALSTACK 
    # Backend blocks don't inherit from the 'provider' block, 
    # Thus I define the endpoints again here.
    endpoint                    = "http://localhost:4566"
    iam_endpoint                = "http://localhost:4566"
    sts_endpoint                = "http://localhost:4566"
    dynamodb_endpoint           = "http://localhost:4566"
    force_path_style            = true
    skip_credentials_validation = true
    skip_metadata_api_check     = true
  }
}
# Public AWS Provider 
provider "aws" {
  region                      = "us-east-1"
  access_key                  = "test"
  secret_key                  = "test"
  shared_credentials_files = 
  profile = 
  skip_credentials_validation = true
  skip_metadata_api_check     = true
  skip_requesting_account_id  = true
  s3_use_path_style           = true # LocalStack use path-style (s3://bucket/obj)

  endpoints {
    s3             = "http://localhost:4566"
    iam            = "http://localhost:4566"
    secretsmanager = "http://localhost:4566"
    dynamodb       = "http://localhost:4566"
    sns            = "http://localhost:4566"
    sqs            = "http://localhost:4566"
  }
}
# Private Postgres Provider 
provider "postgresql" {
  host     = "localhost"
  port     = 5432
  database = "sensitive_db"
  sslmode  = "disable"
}
