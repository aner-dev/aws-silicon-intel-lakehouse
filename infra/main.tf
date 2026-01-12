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
  source       = "./modules/notifications"
  project_name = var.project_name
}
