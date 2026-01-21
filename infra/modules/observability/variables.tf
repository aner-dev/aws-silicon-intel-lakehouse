variable "service_name" {
  type = string
}

variable "enabled" {
  type = bool
}

variable "tags" {
  type = map(string)
}

variable "alerts_topic_arn" {
  description = "ARN of the SNS topic used for pipeline alerts"
  type        = string
}


