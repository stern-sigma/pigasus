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

