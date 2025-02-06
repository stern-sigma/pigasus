resource "aws_ecr_repository" "dashboard_ecr" {
  name = "pigasus-dashboard"
  image_tag_mutability = "MUTABLE"
  force_delete = true
}

resource "null_resource" "initialise_dashboard_ecr" {
  provisioner "local-exec" {
    command = <<EOT
      aws ecr get-login-password --region eu-west-2 | docker login --username AWS --password-stdin ${local.account_id}.dkr.ecr.eu-west-2.amazonaws.com
      docker build --platform linux/arm64 --provenance false -t pigasus-pipeline .
      docker tag pigasus-pipeline:latest ${aws_ecr_repository.dashboard_ecr.repository_url}:latest
      docker push ${aws_ecr_repository.dashboard_ecr.repository_url}:latest    
    EOT
  }

  depends_on = [aws_ecr_repository.dashboard_ecr]
}
