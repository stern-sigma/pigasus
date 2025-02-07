output "pipeline_ecr_url" {
  value = aws_ecr_repository.pipeline_ecr.repository_url 
}

output "archive_ecr_url" {
  value = aws_ecr_repository.archive_ecr.repository_url
}

output "s3_bucket_name" {
  value = aws_s3_bucket.archive.id
}
  
output "dashboard_ecr_url" {
  value = aws_ecr_repository.dashboard_ecr.repository_url
}
