# --- Storage Module ---
module "storage" {
  source       = "./modules/storage"
  project_name = var.project_name
}

# --- Database Module ---
module "database" {
  source       = "./modules/database"
  project_name = var.project_name
}

# --- Notifications Module ---
module "notifications" {
  source                     = "./modules/notifications"
  project_name               = var.project_name
  pipeline_alerts_topic_name = "data-pipeline-alerts"
}
# --- Observability Module ---
module "observability" {
  source                    = "./modules/observability"
  project_name              = var.project_name
  environment               = var.environment
  pipeline_alerts_topic_arn = module.notifications.pipeline_alerts_topic_arn

}

