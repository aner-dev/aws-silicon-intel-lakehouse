locals {
  # 1. Computed Identity
  name_prefix = "${var.project_name}-${var.environment}"

  # 2. Contextual Metadata
  common_tags = {
    Environment = var.environment
    Project     = var.project_name
    Owner       = "Data-Platform-Team"
    ManagedBy   = "Terraform"
  }

  # 3. Logic Flags 
  # Using simple booleans is cleaner for the "Contract"
  is_production      = var.environment == "prod"
  monitoring_enabled = local.is_production # Directly use the logic
}
