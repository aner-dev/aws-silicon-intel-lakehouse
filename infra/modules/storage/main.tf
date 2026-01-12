terraform {
  required_version = ">= 1.0.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 4.0.0"
    }
  }
}

# --- Rest of your bucket code remains below ---
resource "aws_s3_bucket" "bronze" {
  bucket        = "${var.project_name}-bronze"
  force_destroy = true
}

resource "aws_s3_bucket" "silver" {
  bucket        = "${var.project_name}-silver"
  force_destroy = true
}

resource "aws_s3_bucket" "gold" {
  bucket        = "${var.project_name}-gold"
  force_destroy = true
}
