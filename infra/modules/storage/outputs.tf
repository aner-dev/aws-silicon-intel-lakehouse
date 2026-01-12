output "bucket_ids" {
  # This exports the map of bucket IDs from the module
  value = { for k, b in aws_s3_bucket.layers : k => b.id }
}

