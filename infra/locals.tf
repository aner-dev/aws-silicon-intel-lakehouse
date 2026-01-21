locals {
  # 1. Resource Naming 
  # Purpose: S3 Buckets, IAM Roles, EC2 Names
  resource_name_prefix = "${var.project_name}-${var.environment}"

  # 2. Secret Taxonomy (Slashed)
  # Purpose: Secrets Manager, Parameter Store (SSM) & Self-Documenting
  secret_path_prefix = "/${var.project_name}/${var.environment}"

  # 3. Common Tags
  common_tags = {
    Project     = var.project_name
    Environment = var.environment
    ManagedBy   = "Terraform"
    Repository  = "aws-silicon-intel-lakehouse"
    Team        = "Data-Engineering"
  }
}

