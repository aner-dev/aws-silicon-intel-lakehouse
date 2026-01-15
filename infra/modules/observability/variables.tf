variable "project_name" {
  description = "Name of the project for resource naming"
  type        = string
}

variable "environment" {
  description = "Development, Staging, or Production"
  type        = string
}

variable "pipeline_alerts_topic_arn" {
  description = "ARN of the SNS topic used for pipeline alerts"
  type        = string
}

