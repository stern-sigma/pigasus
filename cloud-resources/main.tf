data "aws_vpc" "c15-vpc" {
  id = var.AWS_VPC_ID
}

resource "aws_ecr_repository" "pipeline_ecr" {
  name = "pigasus-pipeline"
  image_tag_mutability = "MUTABLE"
  force_delete = true
}
