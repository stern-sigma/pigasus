variable "AWS_VPC_ID" {
  type = string
}

variable "pipeline_lambda_security_group_ports" {
  type = list(number)
  default = [
    80,
    443,
    1433
  ]
}

variable "DB_HOST" {
  type = string
}

variable "DB_PORT" {
  type = number
}

variable "DB_PASSWORD" {
  type = string
}

variable "DB_USER" {
  type = string
}

variable "DB_NAME" {
  type = string
}

variable "SCHEMA_NAME" {
  type = string
}

variable "public_subnet_ids" {
  type = list(string)
}
