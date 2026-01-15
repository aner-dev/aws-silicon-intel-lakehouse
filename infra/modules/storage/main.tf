# define the layers locally or via variables
variable "layers" {
  type    = list(string)
  default = ["bronze", "silver", "gold"]
}

resource "aws_s3_bucket" "medallion" {
  # Create one bucket FOR EACH item in the list
  for_each = toset(var.layers)

  # each.key will be "bronze", then "silver", etc.
  bucket        = "${var.bucket_prefix}-${each.key}"
  force_destroy = true

  tags = merge(var.tags, {
    Layer = each.key
  })
}

