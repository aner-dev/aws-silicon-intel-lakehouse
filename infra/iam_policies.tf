# BronzeIngestor IAM permissions 
# 1. THE DATA BLOCK (The "Shopping List") | IAM Authorization: Permissions (WHAT)
data "aws_iam_policy_document" "bronze_ingestor_permissions" {
  statement {
    sid       = "AllowBronzeAccess"
    actions   = ["s3:PutObject", "s3:ListBucket"]
    resources = [module.storage.bronze_bucket_arn, "${module.storage.bronze_bucket_arn}/*"]
  }
  statement {
    actions   = ["dynamodb:PutItem"]
    resources = [module.database.audit_table_arn]
  }
}

# 2. THE TRUST BLOCK (The "Identity Card") | IAM Authentication: AssumeRole (WHO)
data "aws_iam_policy_document" "bronze_trust_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"] # Or "lambda.amazonaws.com"
    }
  }
}

# 3. THE FOUNDATION CALL (Using the module)
module "iam_bronze" {
  source             = "./modules/iam"
  role_name          = "bronze-ingestor-role"
  assume_role_policy = data.aws_iam_policy_document.bronze_trust_policy.json
  iam_policy_json    = data.aws_iam_policy_document.bronze_ingestor_permissions.json
}
# SilverIngestor IAM permissions 
# 1. THE DATA BLOCK (The "Shopping List") | IAM Authorization: Permissions (WHAT)
data "aws_iam_policy_document" "silver_ingestor_permissions" {
  # 1. READ from Bronze 
  statement {
    sid       = "ReadBronzeSource" # Statement ID 
    actions   = ["s3:GetObject", "s3:ListBucket"]
    resources = [module.storage.bronze_bucket_arn, "${module.storage.bronze_bucket_arn}/*"]
  }

  # 2. WRITE/MANAGE Silver (Iceberg optimized)
  statement {
    sid       = "ManageSilverIceberg"
    actions   = ["s3:PutObject", "s3:GetObject", "s3:ListBucket", "s3:DeleteObject"]
    resources = [module.storage.silver_bucket_arn, "${module.storage.silver_bucket_arn}/*"]
  }

  # 3. OBSERVABILITY
  statement {
    sid       = "AuditLogs"
    actions   = ["dynamodb:PutItem", "dynamodb:UpdateItem"]
    resources = [module.database.audit_table_arn]
  }
}


# 2. THE TRUST BLOCK (The "Identity Card") | IAM Authentication: AssumeRole (WHO)
data "aws_iam_policy_document" "silver_trust_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["glue.amazonaws.com"] # Or "lambda.amazonaws.com"
    }
  }
}

# 3. THE FOUNDATION CALL (Using the module)
module "iam_silver" {
  source             = "./modules/iam"
  role_name          = "silver-ingestor-role"
  assume_role_policy = data.aws_iam_policy_document.silver_trust_policy.json
  iam_policy_json    = data.aws_iam_policy_document.silver_ingestor_permissions.json
}

# 1. THE DATA BLOCK (The "Shopping List")
data "aws_iam_policy_document" "observability_manager_permissions" {

  # Permission to update the Audit Ledger (DynamoDB)
  statement {
    sid = "WriteAuditLedger"
    actions = [
      "dynamodb:PutItem",
      "dynamodb:UpdateItem",
      "dynamodb:GetItem",
      "dynamodb:Query"
    ]
    resources = [module.database.audit_table_arn]
  }

  # Permission to send Alerts (SNS)
  statement {
    sid       = "PublishAlerts"
    actions   = ["sns:Publish"]
    resources = [module.notifications.alerts_topic_arn]
  }

  # Permission to write application logs (CloudWatch)
  statement {
    sid = "WriteLogs"
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    resources = ["*"] # Best practice: Narrow this to your Log Group ARN
  }
}

# 2. THE TRUST BLOCK (The "Identity Card")
# I'll reuse the "allow_localstack_services" from before or create a specific one
data "aws_iam_policy_document" "observability_trust_policy" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com", "events.amazonaws.com"]
    }
  }
}

# 3. THE FOUNDATION CALL (Executing the Factory)
module "iam_observability" {
  source             = "./modules/iam"
  role_name          = "observability-manager"
  assume_role_policy = data.aws_iam_policy_document.observability_trust_policy.json
  iam_policy_json    = data.aws_iam_policy_document.observability_manager_permissions.json
}

