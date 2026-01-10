# 1. Your Lakehouse Internal Buckets (The ones you were missing)
resource "aws_s3_bucket" "layers" {
  for_each = toset(["bronze", "silver", "gold"])
  bucket   = "silicon-intel-${each.value}"
}

# 2. The Mock Source Bucket for NYC Taxi
resource "aws_s3_bucket" "nyc_taxi_source" {
  bucket = "nyc-tlc"
}

# 3. Keep this for compatibility if needed
resource "aws_s3_bucket" "reviews_source" {
  bucket = "amazon-reviews-pds"
}
