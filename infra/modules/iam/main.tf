# The Policy (The "What")
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
