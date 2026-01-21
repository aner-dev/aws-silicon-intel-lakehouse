#!/bin/bash

# --- CONFIGURATION ---
REGION="us-east-1"
ENDPOINT="http://localhost:4566"
BUCKET_NAME="terraform-state-bucket"
TABLE_NAME="terraform-state-lock"

echo "  Starting LocalStack Bootstrap for Terraform Backend..."

# 1. Create S3 Bucket for State
if aws --endpoint-url=$ENDPOINT s3api head-bucket --bucket "$BUCKET_NAME" 2>/dev/null; then
  echo " 󰗠 S3 bucket '$BUCKET_NAME' already exists."
else
  echo " 🪣 Creating S3 bucket '$BUCKET_NAME'..."
  aws --endpoint-url=$ENDPOINT s3api create-bucket --bucket "$BUCKET_NAME" --region $REGION
fi

# 2. Create DynamoDB Table for Locking
if aws --endpoint-url=$ENDPOINT dynamodb describe-table --table-name "$TABLE_NAME" 2>/dev/null; then
  echo "󰗠  DynamoDB table '$TABLE_NAME' already exists."
else
  echo "🔑 Creating DynamoDB table '$TABLE_NAME'..."
  aws --endpoint-url=$ENDPOINT dynamodb create-table \
    --table-name "$TABLE_NAME" \
    --attribute-definitions AttributeName=LockID,AttributeType=S \
    --key-schema AttributeName=LockID,KeyType=HASH \
    --provisioned-throughput ReadCapacityUnits=5,WriteCapacityUnits=5 \
    --endpoint-url=$ENDPOINT
fi

echo "🎊 Bootstrap complete! You can now run 'terraform init'."
