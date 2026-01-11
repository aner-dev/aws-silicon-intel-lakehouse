# --- SETTINGS ---
TERRAFORM_DIR = ./infra

.PHONY: help setup astro-start ingest ingest-news ingest-taxi \
        transform transform-news transform-taxi multiply seed

help:
	@echo "Silicon Intel Lakehouse - Development Menu"
	@echo "  make setup           Build Infrastructure + Start Airflow"
	@echo "  make ingest          Ingest ALL data"
	@echo "  make transform       Transform ALL data"
	@echo "  make seed            Full Data Population (Ingest + Transform)"

# --- 1. PLATFORM ---
setup:
	@echo "🌌 Starting Astronomer (Airflow + LocalStack)..."
	astro dev start --verbosity debug
	@echo "⏳ Waiting for LocalStack API to be ready..."
	@echo "🏗️  Provisioning AWS Infra via Terraform..."
	cd $(TERRAFORM_DIR) && terraform init && terraform apply -auto-approve
	@echo "✅ PLATFORM READY."

# --- 2. BRONZE LAYER (Ingestion) ---
ingest-news:
	@echo "📥 Ingesting News..."
	uv run src/extract/bronze_ingestion_news_api.py

ingest-taxi:
	@echo "📥 Ingesting Taxi..."
	uv run src/extract/bronze_ingestion_taxi.py

ingest: ingest-news ingest-taxi
	@echo "✅ Bronze Layer Complete."

# --- 3. SILVER LAYER (Transformation) ---
transform-news:
	@echo "💎 Transforming News..."
	uv run src/transform/silver_transform_pyspark_news_api.py

transform-taxi:
	@echo "💎 Transforming Taxi..."
	uv run src/transform/silver_transform_pyspark_taxi.py

transform: transform-news transform-taxi
	@echo "✅ Silver Layer Complete."

# --- 4. MASTER COMMANDS ---
seed: ingest transform multiply
	@echo "🔥 LAKEHOUSE FULLY POPULATED."

multiply:
	@echo "🧪 Running data multiplier..."
	uv run src/utils/data_multiplier.py
