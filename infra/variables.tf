variable "project_name" {
  description = "The prefix used for all naming conventions (NYC Transit project)"
  type        = string
  default     = "aws-mobility-elt-pipeline-lakehouse"
}

variable "environment" {
  type    = string
  default = "dev"
}

variable "region" {
  type    = string
  default = "us-east-1"
}
