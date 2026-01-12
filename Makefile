# --- SETTINGS ---
TERRAFORM_DIR = ./infra

.PHONY: help setup run test lint clean

help:
	@echo "NYC Transit Lakehouse - Development Menu"
	@echo "  make setup    Build Infra + Start Airflow/LocalStack"
	@echo "  make run      Execute the full Medallion Pipeline (Metadata-driven)"
	@echo "  make test     Run the Pytest suite"
	@echo "  make lint     Run Static Analysis (Ruff)"

# --- 1. PLATFORM ---
setup:
	@echo "🌌 Checking Astronomer/LocalStack status..."
	@if [ "$$(astro dev ps 2>/dev/null | grep -c 'Up')" -ge 1 ]; then \
		echo "✅ LocalStack is already running."; \
	else \
		echo "🚀 Starting Astronomer (LocalStack)..."; \
		astro dev start; \
		echo "⏳ Waiting 15s for LocalStack to initialize..."; \
		sleep 15; \
	fi
	@echo "🏗️ Provisioning AWS Infra via Terraform..."
	cd $(TERRAFORM_DIR) && terraform init && terraform apply -auto-approve

# --- 2. EXECUTION ---
# This single command now handles everything because your Python code is smart!
run:
	uv run src/run_pipeline.py

test:
	uv run pytest tests/

lint:
	uv run ruff check .
