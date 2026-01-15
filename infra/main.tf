# --- Storage Module ---
module "storage" {
  source      = "./modules/storage"
  bucket_name = "${local.name_prefix}-raw-storage" # The module just takes the string
  tags        = local.common_tags
}

# --- Database Module ---
module "database" {
  source = "./modules/database"
}

# --- Notifications Module ---
module "notifications" {
  source                     = "./modules/notifications"
  topic_name                 = "${local.name_prefix}-alerts"
  tags                       = local.common_tags
  pipeline_alerts_topic_name = "data-pipeline-alerts"
}
# --- Observability Module ---
module "observability" {
  source                    = "./modules/observability"
  service_name              = "${local.name_prefix}-observability"
  enabled                   = local.monitoring_enabled
  tags                      = local.common_tags
  pipeline_alerts_topic_arn = module.notifications.pipeline_alerts_topic_arn

}

# future version 
# infra/main.tf
# All logic is hidden in locals.tf. This file is for ARCHITECTURE.

module "storage" {
  source      = "./modules/storage"
  bucket_name = "${local.name_prefix}-raw-storage"
  tags        = local.common_tags
}

module "database" {
  source = "./modules/database"
  tags   = local.common_tags
}

module "notifications" {
  source     = "./modules/notifications"
  topic_name = "${local.name_prefix}-alerts"
  tags       = local.common_tags
}

module "observability" {
  source                    = "./modules/observability"
  enabled                   = local.monitoring_enabled
  pipeline_alerts_topic_arn = module.notifications.pipeline_alerts_topic_arn
  tags                      = local.common_tags
}
