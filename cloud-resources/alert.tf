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
  policy = data.aws_iam_policy_document.alert_lambda.json
}

resource "aws_lambda_function" "alert" {
  function_name = "pigasus-alert"
  role = aws_iam_role.alert_lambda.arn 

  architectures = ["arm64"]

  package_type = "Image"
  image_uri = "${aws_ecr_repository.alert.repository_url}:latest"

  depends_on = [
    aws_cloudwatch_log_group.alert,
    null_resource.initialise_alert_ecr
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

data "aws_iam_policy_document" "alert_step_role" {
  statement {
    effect = "Allow"

    principals {
      type = "Service"
      identifiers = ["states.amazonaws.com"]
    }

    actions = ["sts:AssumeRole"]
  }
}

resource "aws_iam_role" "alert_step_role" {
  name = "pigasus-alert-step"
  assume_role_policy = data.aws_iam_policy_document.alert_step_role.json
}

resource "aws_iam_role_policy_attachment" "alert_step_role_lambda" {
  role = aws_iam_role.alert_step_role.name 
  policy_arn = "arn:aws:iam::aws:policy/AWSLambda_FullAccess"
}

resource "aws_iam_role_policy_attachment" "alert_step_role_ses" {
  role = aws_iam_role.alert_step_role.name 
  policy_arn = "arn:aws:iam::aws:policy/AmazonSESFullAccess"
}

resource "aws_iam_role_policy_attachment" "alert_step_role_x_ray" {
   role = aws_iam_role.alert_step_role.name
  policy_arn = "arn:aws:iam::aws:policy/AWSXrayFullAccess"
}

resource "aws_sfn_state_machine" "alert" {
  name = "pigasus-alert"
  role_arn = aws_iam_role.alert_step_role.arn
  definition = jsonencode({
  "QueryLanguage": "JSONata",
  "Comment": "A description of my state machine",
  "StartAt": "Lambda Invoke",
  "States": {
    "Lambda Invoke": {
      "Type": "Task",
      "Resource": "arn:aws:states:::lambda:invoke",
      "Output": "{% $states.result.Payload %}",
      "Arguments": {
        "FunctionName": "${aws_lambda_function.alert.arn}",
        "Payload": "{% $states.input %}"
      },
      "Retry": [
        {
          "ErrorEquals": [
            "Lambda.ServiceException",
            "Lambda.AWSLambdaException",
            "Lambda.SdkClientException",
            "Lambda.TooManyRequestsException"
          ],
          "IntervalSeconds": 1,
          "MaxAttempts": 3,
          "BackoffRate": 2,
          "JitterStrategy": "FULL"
        }
      ],
      "Next": "Choice",
      "Assign": {
        "emails": "{% $states.result.Payload %}"
      }
    },
    "Choice": {
      "Type": "Choice",
      "Choices": [
        {
          "Next": "Success",
          "Condition": "{% $count($emails) > 0 %}"
        }
      ],
      "Default": "Map"
    },
    "Success": {
      "Type": "Succeed"
    },
    "Map": {
      "Type": "Map",
      "ItemProcessor": {
        "ProcessorConfig": {
          "Mode": "INLINE"
        },
        "StartAt": "SendEmail",
        "States": {
          "SendEmail": {
            "Type": "Task",
            "Arguments": {
              "Content": {
                "Simple": {
                  "Body": {
                    "Html": {
                      "Data": "{% $emails.email %}"
                    }
                  },
                  "Subject": {
                    "Data": "Telemetry Alert"
                  }
                }
              },
              "Destination": {
                "ToAddresses": [
                  "{% $emails.email_address %}"
                ]
              },
              "FeedbackForwardingEmailAddress": "${var.my_email}",
              "FromEmailAddress": "${var.my_email}"
            },
            "Resource": "arn:aws:states:::aws-sdk:sesv2:sendEmail",
            "End": true
          }
        }
      },
      "Items": "{% $emails %}",
      "Next": "Success (1)"
    },
    "Success (1)": {
      "Type": "Succeed"
    }
  }
}
  )
  type = "STANDARD"
}
