# infra/main.tf 
# THE ROLE (The Costume)
resource "aws_iam_role" "this" {
  name               = var.role_name
  assume_role_policy = var.assume_role_policy # Who can "become" this role?
}


# 2. THE POLICY (The Permissions JSON)
resource "aws_iam_policy" "this" {
  name        = "${var.role_name}-policy"
  description = "Managed policy for ${var.role_name}"
  policy      = var.iam_policy_json
}

# 3. THE ATTACHMENT (The Glue)
resource "aws_iam_role_policy_attachment" "this" {
  role       = aws_iam_role.this.name
  policy_arn = aws_iam_policy.this.arn
}
