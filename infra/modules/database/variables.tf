variable "project_name" {
  type = string
}

variable "audit_table_name" {
  type    = string
  default = "audit"
}

variable "secret_prefix" {
  type        = string
  description = "The path prefix for secrets"
}

variable "tags" {
  type = map(string)
}
