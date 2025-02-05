output "pipeline_ecr_url" {
  value = aws_ecr_repository.pipeline_ecr.repository_url 
}
