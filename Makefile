# --- SETTINGS ---
DOCKER_COMPOSE = podman-compose 
TERRAFORM_DIR  = ./infra

# --- TARGETS DECLARATION (.PHONY) ---
# Declare all commands that do not represent physical files
.PHONY: help up down setup astro-start restart status clean \
        ingest multiply seed dev

# --- 0. MENU ---
help:
	@echo "Silicon Intel Lakehouse - Development Menu"
	@echo "  make up           Start Sidecars only (via Podman)"
	@echo "  make setup        Deploy S3 buckets and Secrets via Terraform"
	@echo "  make astro-start  Start Airflow and Sidecars (Astro)"
	@echo "  make seed         Ingest NewsAPI (Bronze) + Multiply (Silver)"
	@echo "  make dev          FULL BOOTSTRAP (Infra + Data Seeding)"
	@echo "  make status       Check infrastructure health"
	@echo "  make down         Stop everything"
	@echo "  make clean        Wipe infrastructure and Terraform state"

# --- 1. INFRASTRUCTURE & ORCHESTRATION ---
# 'up' is removed as a standalone step in 'dev' since Astro handles container lifecycle.
# It remains available for manually starting sidecars if needed.
up:
	@echo "🚀 Starting Sidecars via Podman..."
	$(DOCKER_COMPOSE) up -d

setup:
	@echo "🏗️ Applying Terraform (LocalStack)..."
	cd $(TERRAFORM_DIR) && terraform init && terraform apply -auto-approve
	@echo "✅ Infrastructure ready."

# --- 2. ORCHESTRATION ---
astro-start:
	@echo "🌌 Starting Astronomer (Airflow + Sidecars)..."
	astro dev start

# --- 3. DATA OPERATIONS ---
ingest:
	@echo "📥 Ingesting seed data..."
	uv run src/extract/bronze_ingestion_news_api.py

multiply:
	@echo "💎 Multiplying data for Silver layer..."
	uv run src/utils/data_multiplier.py

seed: ingest multiply
	@echo "✅ Data seeding completed."

# --- 4. THE MASTER COMMAND (REORDERED) ---
# First we launch Astro (starting LocalStack/Spark), then Terraform, then Seed.
dev: astro-start setup seed
	@echo "🔥 ALL SYSTEMS GO. Lakehouse is populated and ready!"
