# --- SETTINGS ---
TERRAFORM_DIR = ./infra

.PHONY: help setup run test lint clean health-check

help:
	@echo "NYC Transit Lakehouse - Development Menu"
	@echo "  make setup    Build Infra + Start Airflow/LocalStack"
	@echo "  make run      Execute the full Medallion Pipeline (Metadata-driven)"
	@echo "  make test     Run the Pytest suite"
	@echo "  make lint     Run Static Analysis (Ruff)"

# --- 1. PLATFORM ---
setup:
	@echo "  Checking Podman service status..."
	@if ! doas rc-service podman-api-user status > /dev/null 2>&1; then \
		echo "⚠️ Podman is stopped. Starting rc-service..."; \
		doas rc-service podman-api-user start; \
	fi 
	@echo "🌌 Checking Astronomer/LocalStack status..."
	@if [ "$$(astro dev ps 2>/dev/null | grep -c 'Up')" -ge 1 ]; then \
		echo "✅ LocalStack is already running."; \
	else \
		echo "🚀 Starting Astronomer (LocalStack)..."; \
		astro dev start --verbosity debug; \
	fi
	@echo "🥾 Bootstrapping Terraform Backend (S3/DynamoDB)..."
	@chmod +x $(TERRAFORM_DIR)/bootstrap.sh
	@./$(TERRAFORM_DIR)/bootstrap.sh
	@echo "  Boostrap completed!" 
	@echo "🏗️ Provisioning AWS Infra via Terraform..."
	cd $(TERRAFORM_DIR) && terraform init && terraform apply -auto-approve -input=false 

clean-infra:
	@echo "🗑️ Destroying all AWS resources..."
	cd $(TERRAFORM_DIR) && terraform destroy -auto-approve
# --- 2. EXECUTION ---
# This single command now handles everything because your Python code is smart!
run:
	uv run src/run_pipeline.py

test:
	uv run pytest -v tests/

lint:
	uv run ruff check .
