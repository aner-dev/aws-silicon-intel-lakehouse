# ./modules/iam/variables.tf
variable "role_name" {
  description = "The name of the IAM role"
  type        = string
}

variable "assume_role_policy" {
  description = "The JSON trust policy that allows an entity (like Lambda or EC2) to assume this role"
  type        = string
}

variable "iam_policy_json" {
  description = "The JSON permissions policy document to attach to this role"
  type        = string
}

