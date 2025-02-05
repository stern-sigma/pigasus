resource "aws_cloudwatch_log_group" "archive_log_group" {
  name = "/aws/pigasus/lambda/archive"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_ecr_repository" "archive_ecr" {
  name = "pigasus-archive"
  image_tag_mutability = "MUTABLE"
  force_delete = true
}

resource "null_resource" "initialise_archive_ecr" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker build --platform linux/arm64 --provenance false -t pigasus-archive .
      docker tag pigasus-archive:latest ${aws_ecr_repository.archive_ecr.repository_url}:latest
      docker push ${aws_ecr_repository.archive_ecr.repository_url}:latest
    EOT
  }

  depends_on = [aws_ecr_repository.archive_ecr]
}

data "aws_iam_policy_document" "archive_lambda_permissions" {
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

resource "aws_iam_role" "archive_lambda" {
  name = "pigasus-archive-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy" "archive_lambda" {
  name = "pigasus-archive-lambda"
  role = aws_iam_role.archive_lambda.id
  policy = data.aws_iam_policy_document.archive_lambda_permissions.json
}

resource "aws_lambda_function" "archive" {
  function_name = "pigasus-archive"
  role = aws_iam_role.archive_lambda.arn 

  architectures = ["arm64"]

  package_type = "Image"
  image_uri = "${aws_ecr_repository.archive_ecr.repository_url}:latest"

  depends_on = [
    aws_cloudwatch_log_group.archive_log_group,
    null_resource.initialise_archive_ecr
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
    security_group_ids = [
      aws_security_group.pipeline_lambda_security_group.id
    ]
  }
}


data "aws_iam_policy_document" "archive_scheduler_permissions" {
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

resource "aws_iam_role" "archive_scheduler" {
  name = "pigasus-archive-scheduler"
  assume_role_policy = data.aws_iam_policy_document.scheduler_assume.json 
}

resource "aws_iam_role_policy" "archive_scheduler" {
  name = "pigasus-archive-scheduler"
  role = aws_iam_role.archive_scheduler.id
  policy = data.aws_iam_policy_document.archive_scheduler_permissions.json
}

resource "aws_scheduler_schedule" "archive_schedule" {
  name = "pigasus-archive"

  flexible_time_window {
    mode = "OFF"
  }

schedule_expression = "cron(0 * ? * * *)"

  target {
    arn = aws_lambda_function.archive.arn 
    role_arn = aws_iam_role.archive_scheduler.arn
  }
}
