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
