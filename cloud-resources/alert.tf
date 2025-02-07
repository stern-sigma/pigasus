resource "aws_cloudwatch_log_group" "alert" {
  name = "/aws/pigasus/lambda/alert"
  retention_in_days = 7
  lifecycle {
    prevent_destroy = false
  }
}

resource "aws_ecr_repository" "alert" {
  name = "pigasus-alert"
  image_tag_mutability = "MUTABLE"
  force_delete = true
}

resource "null_resource" "initialise_alert_ecr" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker build --platform linux/arm64 --provenance false -t pigasus-alert .
      docker tag pigasus-alert:latest ${aws_ecr_repository.alert.repository_url}:latest
      docker push ${aws_ecr_repository.alert.repository_url}:latest    
    EOT
  }

  depends_on = [aws_ecr_repository.alert]
}

data "aws_iam_policy_document" "alert_lambda" {
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
      "ec2:getSecurityGroupForVpc"
    ]

    resources = [
      "*",
    ]
  }
}

resource "aws_iam_role" "alert_lambda" {
  name = "pigasus-alert-lambda"
  assume_role_policy = data.aws_iam_policy_document.lambda_assume.json
}

resource "aws_iam_role_policy" "alert_lambda" {
  name = "pigasus-alert-lambda"
  role = aws_iam_role.alert_lambda.id
  policy = data.aws_iam_policy_document.alert_lambda_permissions.json
}

resource "aws_lambda_function" "alert" {
  function_name = "pigasus-alert"
  role = aws_iam_role.alert_lambda.arn 

  architectures = ["arm64"]

  package_type = "Image"
  image_uri = "${aws_ecr_repository.alert_ecr.repository_url}:latest"

  depends_on = [
    aws_cloudwatch_log_group.alert_log_group,
    null_resource.alert_pipeline_ecr
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
    security_group_ids = [aws_security_group.alert_lambda_security_group.id]
  }
}


