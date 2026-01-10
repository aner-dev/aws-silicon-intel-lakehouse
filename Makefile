# --- SETTINGS ---
DOCKER_COMPOSE = podman-compose 
TERRAFORM_DIR  = ./infra

# --- TARGETS DECLARATION (.PHONY) ---
# Declare all commands that do not represent physical files
.PHONY: help up down setup astro-start restart status clean \
	ingest ingest-news ingest-reviews \
        transform transform-news transform-reviews \
        multiply seed dev

# --- 0. MENU ---
help:
	@echo "Silicon Intel Lakehouse - Development Menu"
	@echo "  make up            Start Sidecars only (via Podman)"
	@echo "  make setup         Deploy S3 buckets and Secrets via Terraform"
	@echo "  make astro-start   Start Airflow and Sidecars (Astro)"
	@echo "  make ingest        Ingest ALL data (News + Reviews)"
	@echo "  make transform     Transform ALL data (Silver/Iceberg)"
	@echo "  make seed          Full Ingestion + Transformation + Multiply"
	@echo "  make dev           FULL BOOTSTRAP (Orchestration + Infra + Data)"


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

# Bronze Layer (Ingestion)
ingest-news:
	@echo "📥 Ingesting News API data..."
	uv run src/extract/bronze_ingestion_news_api.py

ingest-reviews:
	@echo "📥 Ingesting Amazon Reviews data..."
	uv run src/extract/bronze_ingestion_reviews.py

# Silver Layer (Transformation)
transform-news:
	@echo "💎 Transforming News API to Silver (Iceberg)..."
	uv run src/transform/silver_transform_pyspark_news_api.py

transform-reviews:
	@echo "💎 Transforming Amazon Reviews to Silver (Iceberg)..."
	uv run src/transform/silver_transform_pyspark_amazon_reviews.py

# Combined Commands
ingest: ingest-news ingest-reviews

transform: transform-news transform-reviews

# Keep 'multiply' if you still use that specific data-augmentation script
multiply:
	@echo "🧪 Running data multiplier..."
	uv run src/utils/data_multiplier.py

# Updated Seed: Now it does EVERYTHING
seed: ingest transform multiply
	@echo "✅ Full Data Lakehouse seeding completed."

# --- 4. THE MASTER COMMAND ---
dev: astro-start setup seed
	@echo "🔥 ALL SYSTEMS GO. Lakehouse is populated and ready!"

