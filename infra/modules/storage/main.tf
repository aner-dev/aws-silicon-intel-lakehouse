resource "aws_s3_bucket" "this" {
  for_each = var.buckets

  bucket        = "${var.project_name}-${each.key}"
  force_destroy = true

  # We use merge() here to combine Global Tags with Specific Tags
  tags = merge(var.tags, {
    Name    = "${var.project_name}-${each.key}"
    Layer   = each.key
    Iceberg = each.value.is_iceberg ? "true" : "false"
  })
}

# Apply versioning based on the map value
resource "aws_s3_bucket_versioning" "this" {
  for_each = var.buckets
  bucket   = aws_s3_bucket.this[each.key].id

  versioning_configuration {
    status = each.value.versioning_enabled ? "Enabled" : "Disabled"
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "this" {
  for_each = var.buckets
  bucket   = aws_s3_bucket.this[each.key].id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256" # This uses the default S3 key
    }
  }
}
