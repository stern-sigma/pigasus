data "aws_vpc" "c15-vpc" {
  id = var.AWS_VPC_ID
}

data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
}


data "aws_iam_policy_document" "lambda_assume" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["lambda.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

data "aws_iam_policy_document" "scheduler_assume" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["scheduler.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_security_group" "pipeline_lambda_security_group" {
  name = "pigasus-pipeline-lambda"
  vpc_id = data.aws_vpc.c15-vpc.id

  dynamic "ingress" {
    for_each = var.pipeline_lambda_security_group_ports

    content {
      from_port = ingress.value
      to_port = ingress.value 
      protocol = "tcp"
    }
  }

  dynamic "egress" {
    for_each = var.pipeline_lambda_security_group_ports

    content {
      from_port = egress.value 
      to_port = egress.value 
      protocol = "tcp"
    }
  }
}

