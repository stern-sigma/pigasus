# Cloud Resources Terraform 

A terraform file to initialise all of the cloud resources described in the architecture diagram in `/dev-resources`.

## Getting Started 🔨

For the terraform to work, the following must be set up:

- You must have an AWS account
- You must have a database which is accessible over the internet
- You must have an ECS cluster initialised on your AWS account
- Create a file called 'terraform.tfvars'
- Your terraform.tfvars should have the following format:
  ```HCL
  AWS_VPC_ID = <str: id of your VPC>
  DB_HOST = <str: host of your database>
  DB_PORT = <int: port over which your database runs>
  DB_PASSWORD = <str: your db password>
  DB_USER = <str: your db username>
  SCHEMA_NAME = <str: the schema of your database in which your tables are stored>
  public_subnet_ids = <list(str): a list of ids of subnets for resources to be made avilable from. Must be public and located within the same VPC as your AWS_VPC_ID>
  cluster_arn = <str: the arn of the ECS cluster in which you want any ACS tasks to run>
  my_email = <str: the email which you want to handle alert emails. Must be verified in AWS>
  access_key = <str: you aws access key>
  secret_access_key = <str: your aws secret access key>
  ```
- You must have the Docker daemon running

## Dependencies 🛠️

- [HashiCorp Terraform](https://developer.hashicorp.com/terraform/install?product_intent=terraform)
- [Docker desktop](https://www.docker.com/products/docker-desktop/)
- [AWS CLI](https://docs.aws.amazon.com/cli/latest/userguide/getting-started-install.html)


## Usage 🫡

To deploy the resources, run the following commands:
```bash
terraform init
terraform apply
yes
```
You will generate several outputs, which can then be used to configure the environments of your cloud resources, or to deploy your images.
