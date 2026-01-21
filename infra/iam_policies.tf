# Blueprint Formula: 2 Data Blocks (the logic) + 1 Instance of the Module 

# --- BRONZE LAYER (The Ingestor) ---

data "aws_iam_policy_document" "bronze_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"] # Only Lambda can ingest
    }
  }
}

data "aws_iam_policy_document" "bronze_permissions" {
  statement {
    sid       = "AllowBronzeAccess"
    actions   = ["s3:PutObject", "s3:ListBucket"]
    resources = [module.storage.bronze_bucket_arn, "${module.storage.bronze_bucket_arn}/*"]
  }
  statement {
    sid       = "WriteAuditLedger"
    actions   = ["dynamodb:PutItem"]
    resources = [module.database.audit_table_arn]
  }
}

module "iam_bronze" {
  source             = "./modules/iam"
  role_name          = "${local.name_prefix}-bronze-role"
  assume_role_policy = data.aws_iam_policy_document.bronze_trust.json
  iam_policy_json    = data.aws_iam_policy_document.bronze_permissions.json
}

# --- SILVER LAYER (The Transformer / Iceberg) ---

data "aws_iam_policy_document" "silver_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ecs-tasks.amazonaws.com"] # Example: Silver runs in Docker/ECS
    }
  }
}

data "aws_iam_policy_document" "silver_permissions" {
  statement {
    sid       = "ReadBronze"
    actions   = ["s3:GetObject", "s3:ListBucket"]
    resources = [module.storage.bronze_bucket_arn, "${module.storage.bronze_bucket_arn}/*"]
  }

  statement {
    sid       = "ManageSilverIceberg"
    actions   = ["s3:PutObject", "s3:GetObject", "s3:ListBucket", "s3:DeleteObject"]
    resources = [module.storage.silver_bucket_arn, "${module.storage.silver_bucket_arn}/*"]
  }
  statement {
    sid       = "UpdateAuditLedger"
    actions   = ["dynamodb:UpdateItem"]
    resources = [module.database.audit_table_arn]
  }
}

module "iam_silver" {
  source             = "./modules/iam"
  role_name          = "${local.name_prefix}-silver-role"
  assume_role_policy = data.aws_iam_policy_document.silver_trust.json
  iam_policy_json    = data.aws_iam_policy_document.silver_permissions.json
}


# =================================================
# 3. OBSERVABILITY: Monitoring + Alerts
# =================================================

data "aws_iam_policy_document" "obs_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }
  }
}

data "aws_iam_policy_document" "obs_permissions" {
  # 1. Full Audit Ledger Access (Matches log_status and internal queries)
  statement {
    sid = "ManageAuditLedger"
    actions = [
      "dynamodb:PutItem", # Required for obs.log_status()
      "dynamodb:UpdateItem",
      "dynamodb:GetItem", # Required for internal validation
      "dynamodb:Query"
    ]
    resources = [module.database.audit_table_arn]
  }

  # 2. Alerts (Matches notify_failure)
  statement {
    sid       = "PublishPipelineAlerts"
    actions   = ["sns:Publish"]
    resources = [module.notifications.alerts_topic_arn]
  }

  # 3. Logging (Required for the 'log' utility in your Python script)
  statement {
    sid = "WriteApplicationLogs"
    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]
    # Restrict to the project's log groups for better security
    resources = ["arn:aws:logs:*:*:log-group:/aws/lambda/${local.name_prefix}-*"]
  }
}



module "iam_observability" {
  source             = "./modules/iam"
  role_name          = "${local.name_prefix}-obs-manager"
  assume_role_policy = data.aws_iam_policy_document.obs_trust.json
  iam_policy_json    = data.aws_iam_policy_document.obs_permissions.json
}

