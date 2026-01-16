# infra/main.tf
module "iam_bronze" {
  source             = "./modules/iam"
  role_name          = "bronze-ingestor"
  assume_role_policy = data.aws_iam_policy_document.allow_localstack_services.json
  iam_policy_json    = data.aws_iam_policy_document.bronze_ingestor.json
}

# Create the Policy from the JSON we passed in
resource "aws_iam_policy" "this" {
  name   = "${var.role_name}-policy"
  policy = var.iam_policy_json
}

# Create the Role
resource "aws_iam_role" "this" {
  name               = var.role_name
  assume_role_policy = var.assume_role_policy # Who can "become" this role?
}

# Attach them
resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.this.arn
}

# 1. Create the Custom Policy
module "custom_policy" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
  version = "~> 6.0"

  name   = "${var.name_prefix}-${var.role_name}-policy"
  policy = var.policy_json # Injected from outside
}

# 2. Create the Role and Attach the Policy
module "iam_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role"
  version = "~> 6.0"

  role_name = "${var.name_prefix}-${var.role_name}-role"

  # The "Agnostic" part: Trust whatever service we pass in (glue, lambda, etc.)
  trusted_role_services = var.trusted_services

  # Attach the policy we just made above
  custom_role_policy_arns = [module.custom_policy.arn]
}

module "silver_iam_role" {
  source = "./modules/iam"

  role_name        = "silver-transformer"
  trusted_services = ["glue.amazonaws.com"]

  # Use .json to convert the Data Source into the string the module expects
  policy_json = data.aws_iam_policy_document.silver_layer_permissions.json
}


module "lakehouse_processing_policy" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-policy"
  version = "~> 6.0"

  name        = "LakehouseProcessingPolicy"
  description = "Allows transformation from Bronze to Silver"

  # Use jsonencode for clean, Python-like dictionary syntax
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action   = ["s3:GetObject", "s3:ListBucket"]
        Effect   = "Allow"
        Resource = ["arn:aws:s3:::bronze-bucket", "arn:aws:s3:::bronze-bucket/*"]
      },
      {
        Action   = ["s3:PutObject", "s3:Merge*"] # Iceberg needs Merge
        Effect   = "Allow"
        Resource = ["arn:aws:s3:::silver-bucket", "arn:aws:s3:::silver-bucket/*"]
      }
    ]
  })
}

# The Role (The "Who" - Service)
module "spark_role" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-role"
  version = "~> 6.0"

  name = "SparkMedallionRole"

  # This is the "Trust Relationship"
  # It says: "I allow the GLUE service to assume this role"
  trusted_role_services = ["glue.amazonaws.com"]

  # Attaching the Policy we created above
  custom_role_policy_arns = [module.lakehouse_processing_policy.arn]
}

# PILLAR 3: The User (The "Who" - Human)
module "admin_user" {
  source  = "terraform-aws-modules/iam/aws//modules/iam-user"
  version = "~> 6.0"

  name = "data-engineer-local"

  # Useful for LocalStack to get keys for your .env file
  create_iam_user_login_profile = false
  create_iam_access_key         = true
}
