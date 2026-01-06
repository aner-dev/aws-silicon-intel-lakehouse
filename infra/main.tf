# terraform/main.tf
resource "aws_s3_bucket" "layers" {
  for_each = toset(["bronze", "silver", "gold"])
  bucket   = "silicon-intel-${each.value}"
}
