variable "bucket_name" {
  description = "The computed name for the S3 bucket"
  type        = string
}

variable "tags" {
  description = "Standard metadata tags"
  type        = map(string)
}
