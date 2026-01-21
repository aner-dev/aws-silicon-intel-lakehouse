# --- 1. STORAGE ---
module "storage" {
  source       = "./modules/storage"
  project_name = local.name_prefix
  tags         = local.common_tags
  buckets = {
    "bronze" = { versioning_enabled = false, is_iceberg = false },
    "silver" = { versioning_enabled = true, is_iceberg = true },
    "gold"   = { versioning_enabled = true, is_iceberg = true }
  }
}

# --- 2. DATABASE ---
module "database" {
  source           = "./modules/database"
  project_name     = local.name_prefix
  secret_prefix    = local.secret_path_format # From your locals.tf
  audit_table_name = "${local.name_prefix}-audit"
  tags             = local.common_tags
}

# --- 3. NOTIFICATIONS ---
module "notifications" {
  source                     = "./modules/notifications"
alerts_topic_name = "${local.name_prefix}-alerts"
  tags                       = local.common_tags
}

# --- 4. IAM (The Missing Factory Calls) ---
# Calling the IAM factory for each role needed

module "iam_observability" {
  source             = "./modules/iam"
  role_name          = "${local.name_prefix}-observability-role"
  assume_role_policy = data.aws_iam_policy_document.obs_trust.json
  iam_policy_json    = data.aws_iam_policy_document.obs_permissions.json
}

module "iam_silver_processing" {
  source             = "./modules/iam"
  role_name          = "${local.name_prefix}-silver-transformer"
  assume_role_policy = data.aws_iam_policy_document.silver_trust.json # Define in iam_policies.tf
  iam_policy_json    = data.aws_iam_policy_document.silver_permissions.json
}
