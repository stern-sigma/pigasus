resource "aws_ecr_repository" "dashboard_ecr" {
  name = "pigasus-dashboard"
  image_tag_mutability = "MUTABLE"
  force_delete = true
}

resource "null_resource" "initialise_dashboard_ecr" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker build --platform linux/arm64 --provenance false -t pigasus-dashboard .
      docker tag pigasus-dashbaord:latest ${aws_ecr_repository.dashboard_ecr.repository_url}:latest
      docker push ${aws_ecr_repository.dashboard_ecr.repository_url}:latest
    EOT
  }

  depends_on = [aws_ecr_repository.dashboard_ecr]
}

resource "aws_security_group" "dashboard" {
  name = "pigasus-dashboard"
  vpc_id = data.aws_vpc.c15-vpc.id 

  dynamic "ingress" {
    for_each = var.dashboard_sg_ports

    content {
      from_port = ingress.value
      to_port = ingress.value 
      protocol = "tcp"
    }
  }

  dynamic "egress"{
    for_each = var.dashboard_sg_ports

    content {
      from_port = egress.value 
      to_port = egress.value 
      protocol = "tcp"
    }
  }
}

resource "aws_ecs_task_definition" "dashboard" {
  family = "pigasus-dahsboard"
  requires_compatibilities = ["FARGATE"]
  network_mode = "awsvpc"
  cpu = 256
  memory = 512
  execution_role_arn = "arn:aws:iam::129033205317:role/ecsTaskExecutionRole"
  container_definitions = <<TASK_DEFINITION
  [
    {
      "name": "pigasus-dahsboard",
      "image": "${aws_ecr_repository.dashboard_ecr.repository_url}:latest",
      "cpu": 256,
      "memory": 512,
      "essential": true,
      "environment": [
            {
                "name": "DB_NAME",
                "value": "${var.DB_NAME}"
            },
            {
                "name": "DB_HOST",
                "value": "${var.DB_HOST}"
            },
            {
                "name": "DB_PORT",
                "value": "${var.DB_PORT}"
            },
            {
                "name": "DB_USER",
                "value": "${var.DB_USER}"
            },
            {
                "name": "DB_PASSWORD",
                "value": "${var.DB_PASSWORD}"
            },
            {
                "name": "SCHEMA_NAME",
                "value": "${var.SCHEMA_NAME}"
            }
        ],
      "portMappings": [
          {
            "containerPort": 8501,
            "hostPort": 8501
          },
          {
            "containerPort": 1433,
            "hostPort": 1433
          },
          {
            "containerPort": 80,
            "hostPort": 80
          },
          {
            "containerPort": 443,
            "hostPort": 443
          }
        ]
    }
  ]
  TASK_DEFINITION

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture = "X86_64"
  }
}

resource "aws_alb" "dashboard" {
  name = "pigasus-dashboard"
  internal = false
  load_balancer_type = "application"
  security_groups = [aws_security_group.dashboard.id]
  subnets = var.public_subnet_ids
  enable_deletion_protection = false
}

resource "aws_lb_target_group" "dashboard" {
  name        = "pigasus-dashboard"
  target_type = "alb"
  port        = 80
  protocol    = "TCP"
  vpc_id      = data.aws_vpc.c15-vpc.id
}

resource "aws_ecs_service" "dashboard" {
  name = "pigasus-dashboard"
  cluster = var.cluster_arn
  task_definition = aws_ecs_task_definition.dashboard.id 
  force_delete = true 
  launch_type = "FARGATE"
  desired_count = 1 
  network_configuration {
    subnets = var.public_subnet_ids
    security_groups = [aws_security_group.dashboard.id]
    assign_public_ip = true
  }
  load_balancer {
    target_group_arn = aws_lb_target_group.dashboard.arn 
    container_name = "pigasus-dashboard"
    container_port = 8501
  }
}
