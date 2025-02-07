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
