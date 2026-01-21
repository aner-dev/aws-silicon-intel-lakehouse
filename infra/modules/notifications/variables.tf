# modules/notifications/variables.tf

variable "alerts_topic_name" {
  description = "Name of the SNS topic"
  type        = string
}

variable "tags" {
  description = "Common tags for resources"
  type        = map(string)
  default     = {}
}
