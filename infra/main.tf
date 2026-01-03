# Buckets para las capas del Lakehouse
resource "aws_s3_bucket" "bronze" {
  bucket = "silicon-intel-bronze"
}

resource "aws_s3_bucket" "silver" {
  bucket = "silicon-intel-silver"
}

resource "aws_s3_bucket" "gold" {
  bucket = "silicon-intel-gold"
}

# Glue Catalog for Spark Iceberg knows where the tables are 
resource "aws_glue_catalog_database" "semiconductor_db" {
  name = "market_intelligence"
}
