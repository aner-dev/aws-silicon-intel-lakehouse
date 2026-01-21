variable "bucket_name" {
  description = "The computed name for the S3 bucket"
  type        = string
}

variable "tags" {
  type        = map(string)
  default     = {}
  description = "Common tags to apply to all resources"
}

variable "buckets" {
  type = map(object({
    versioning_enabled = bool
    lifecycle_days     = number
    is_iceberg         = bool # Extra flag for documentation/tagging
  }))
  description = "Configuration map for the Lakehouse layers"
}

