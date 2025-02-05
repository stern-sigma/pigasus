data "aws_vpc" "c15-vpc" {
  id = var.AWS_VPC_ID
}

resource "aws_cloudwatch_log_group" "pipeline_log_group" {
  name = "/aws/pigasus/lambda/pipeline"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

data "aws_caller_identity" "current" {}

locals {
  account_id = data.aws_caller_identity.current.account_id
}

resource "aws_ecr_repository" "pipeline_ecr" {
  name = "pigasus-pipeline"
  image_tag_mutability = "MUTABLE"
  force_delete = true
}

resource "null_resource" "docker_build_and_push" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker build --platform linux/arm64 --provenance false -t pigasus-pipeline .
      docker tag pigasus-pipeline:latest ${aws_ecr_repository.pipeline_ecr.repository_url}:latest
      docker push ${aws_ecr_repository.pipeline_ecr.repository_url}:latest    
    EOT
  }

  depends_on = [aws_ecr_repository.pipeline_ecr]
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
      "logs:PutLogEvents",
      "ec2:CreateNetworkInterface",
      "ec2:DescribeNetworkInterfaces",
      "ec2:DescribeSubnets",
      "ec2:DeleteNetworkInterface",
      "ec2:AssignPrivateIpAddresses",
      "ec2:UnassignPrivateIpAddresses",
      "ec2:DescribeSecurityGroups",
      "ec2:DescribeSubnets",
      "ec2:DescribeVpcs",
      "ec2:getSecrutiyGroupForVpc"
    ]

    resources = [
      "*",
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

resource "aws_lambda_function" "pipeline" {
  function_name = "pigasus-pipeline"
  role = aws_iam_role.pipeline_lambda.arn 

  architectures = ["arm64"]

  package_type = "Image"
  image_uri = "${aws_ecr_repository.pipeline_ecr.repository_url}:latest"

  depends_on = [
    aws_cloudwatch_log_group.pipeline_log_group
  ]

  environment {
    variables = {
    DB_HOST = "${var.DB_HOST}",
    DB_PORT = "${var.DB_PORT}",
    DB_PASSWORD = "${var.DB_PASSWORD}",
    DB_USER = "${var.DB_USER}",
    DB_NAME = "${var.DB_NAME}",
    SCHEMA_NAME = "${var.SCHEMA_NAME}"
    }
  }

  vpc_config {
    subnet_ids = var.public_subnet_ids
    security_group_ids = [aws_security_group.pipeline_lambda_security_group.id]
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

data "aws_iam_policy_document" "pipeline_scheduler_permissions" {
  statement {
    effect = "Allow"

    actions = [
      "lambda:InvokeFunction"
    ]

    resources = [
      "*"
    ]
  }
}

resource "aws_iam_role" "pipeline_scheduler" {
  name = "pigasus-pipeline-scheduler"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume.json 
}

resource "aws_iam_role_policy" "pipeline_scheduler" {
  name = "pigasus-pipeline-scheduler"
  role = aws_iam_role.pipeline_scheduler.id
  policy = data.aws_iam_policy_document.pipeline_scheduler_permissions.json
}


