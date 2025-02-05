data "aws_vpc" "c15-vpc" {
  id = var.AWS_VPC_ID
}

resource "aws_ecr_repository" "pipeline_ecr" {
  name = "pigasus-pipeline"
  image_tag_mutability = "MUTABLE"
  force_delete = true
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

data "aws_iam_policy_document" "pipeline_lambda_permissions" {
  statement {
    effect = "Allow"
    
    actions = [
      "logs:CreateLogStream",
      "logs:PutLogEvents"
    ]

    resources = [
      "*"
    ]
  }
}

resource "aws_iam_role" "pipeline_lambda" {
  name = "pigasus-pipeline-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy" "pipeline_lambda" {
  name = "pigasus-pipeline-lambda"
  role = aws_iam_role.pipeline_lambda.id
  policy = data.aws_iam_policy_document.pipeline_lambda_permissions.json
}

resource "aws_security_group" "pipeline_lambda_security_group" {
  name = "pigasus-pipeline-lambda"

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
