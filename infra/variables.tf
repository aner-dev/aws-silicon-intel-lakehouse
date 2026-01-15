variable "project_name" {
  description = "Project identifier"
  type        = string
  default     = "aws-mobility-elt-pipeline-lakehouse"
}

variable "environment" {
  description = "Deployment environment (local, dev, prod)"
  type        = string
  default     = "dev"
}

variable "region" {
  type    = string
  default = "us-east-1"
}
