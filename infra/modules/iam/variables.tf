# ./modules/iam/variables.tf
variable "role_name" {
  description = "Name of the IAM role"
  type        = string
}

variable "assume_role_policy" {
  description = "The policy that allows an entity (like Lambda or EC2) to assume this role"
  type        = string
}

variable "iam_policy_json" {
  description = "The JSON policy document to attach to this role"
  type        = string
}

