variable "topic_name" {
  type = string
}

variable "tags" {
  type = map(string)
}

# Note: You can keep this if you want a hardcoded default, 
# but it's better to pass it from the root locals!
variable "pipeline_alerts_topic_name" {
  description = "Name of the SNS topic used for pipeline alerts"
  type        = string
}
