# --- Storage Module ---
module "storage" {
  source = "./modules/storage"
}

# --- Database Module ---
module "database" {
  source = "./modules/database"
}

module "notifications" {
  source = "./modules/notifications"
}

# --- Secrets (Keep in Root or move to a module if complex) ---
# (Keep your secrets.tf as is for now if it's small)
