locals {
  layer_info = {
    bronze = "Raw immutable data lakehouse layer"
    silver = "Cleaned and transformed Iceberg tables"
    gold   = "Business-ready aggregates and star schema"
  }
}

resource "aws_s3_bucket" "layers" {
  for_each = local.layer_info
  bucket   = "silicon-intel-${each.key}"

  tags = {
    Project     = "Silicon-Intel"
    Layer       = each.key
    Description = each.value
  }
}

resource "aws_s3_bucket_versioning" "gold_versioning" {
  bucket = aws_s3_bucket.layers["gold"].id
  versioning_configuration {
    status = "Enabled"
  }
}
