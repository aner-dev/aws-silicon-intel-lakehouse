variable "project_name" {
  type    = string
  default = "aws-mobility-elt-pipeline"
}

variable "pipeline_alerts_topic_name" {
  description = "Name of the SNS topic used for pipeline alerts"
  type        = string
}

