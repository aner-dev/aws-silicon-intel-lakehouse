# --- SETTINGS ---
DOCKER_COMPOSE = podman-compose 
TERRAFORM_DIR = ./infra

# --- COMMANDS ---
.PHONY: help up down setup astro-start restart status clean

help:
	@echo "Silicon Intel Lakehouse - Development Menu"
	@echo "  make up          Start LocalStack and Spark (Sidecars)"
	@echo "  make setup       Deploy S3 buckets and Secrets via Terraform"
	@echo "  make astro-start Start Airflow (Astro)"
	@echo "  make dev         FULL BOOTSTRAP (The 'Start of Day' command)"
	@echo "  make status      Check infrastructure health"
	@echo "  make down        Stop everything"

# 1. Start Docker/Podman Sidecars
up:
	@echo "🚀 Starting Sidecar Infrastructure..."
	$(DOCKER_COMPOSE) up -d localstack spark-master spark-worker
	@echo "⏳ Waiting for LocalStack..."
	@sleep 7

# 2. Deploy Infrastructure
setup:
	@echo "🏗️ Applying Terraform (LocalStack)..."
	cd $(TERRAFORM_DIR) && terraform init && terraform apply -auto-approve
	@echo "✅ Infrastructure ready."

# 3. Start Orchestrator
astro-start:
	@echo "🌌 Starting Astronomer Airflow..."
	astro dev start

# 4. FULL START (Your Daily Command)
dev: up setup astro-start
	@echo "🔥 ALL SYSTEMS GO. Happy Coding!"

# 5. Monitoring
status:
	@echo "--- CONTAINERS ---"
	podman ps
	@echo "--- S3 BUCKETS ---"
	@AWS_ENDPOINT_URL=http://localhost:4566 aws s3 ls
	@echo "--- SECRETS ---"
	@AWS_ENDPOINT_URL=http://localhost:4566 aws secretsmanager list-secrets

# 6. Stop/Clean
down:
	$(DOCKER_COMPOSE) down
	astro dev stop

clean: down
	@echo "🧹 Cleaning up terraform state..."
	rm -rf $(TERRAFORM_DIR)/.terraform
	rm -f $(TERRAFORM_DIR)/terraform.tfstate*
