```terraform
# modules/vpc/main.tf
module "vpc" {
  source  = "./modules/vpc"
  region  = var.region
  cidr    = var.vpc_cidr
  name    = var.vpc_name
  azs     = var.azs
}


# modules/vpc/variables.tf
variable "region" {
  type = string
  description = "AWS Region"
  default = "us-east-1"
}

variable "vpc_cidr" {
  type = string
  description = "VPC CIDR Block"
  default = "10.0.0.0/16"
}

variable "vpc_name" {
  type = string
  description = "VPC Name"
  default = "sharepoint-vpc"
}

variable "azs" {
  type = list(string)
  description = "Availability Zones"
  default = ["us-east-1a", "us-east-1b", "us-east-1c"]
}


# modules/vpc/outputs.tf
output "vpc_id" {
  value = module.vpc.vpc_id
}

output "subnet_ids" {
  value = module.vpc.subnet_ids
}

# modules/rds/main.tf
module "rds" {
  source  = "./modules/rds"
  region  = var.region
  instance_type = var.instance_type
  db_name       = var.db_name
  username      = var.username
  password      = var.password
  subnet_ids    = module.vpc.subnet_ids
  engine        = var.engine

}

# modules/rds/variables.tf
variable "region" {
  type = string
  description = "AWS Region"
  default = "us-east-1"
}

variable "instance_type" {
  type = string
  description = "RDS Instance Type"
  default = "db.t3.micro"
}

variable "db_name" {
  type = string
  description = "RDS Database Name"
  default = "sharepoint_db"
}

variable "username" {
  type = string
  description = "RDS Username"
  default = "admin"
}

variable "password" {
  type = string
  description = "RDS Password"
  default = "password123" #Please change this in production
}

variable "engine" {
  type = string
  description = "RDS Engine (MySQL or PostgreSQL)"
  default = "mysql"
}


# modules/rds/outputs.tf
output "rds_endpoint" {
  value = module.rds.db_endpoint
}


# modules/ec2/main.tf
module "ec2" {
  source  = "./modules/ec2"
  region      = var.region
  ami         = var.ami
  instance_type = var.instance_type
  count       = var.instance_count
  subnet_ids  = module.vpc.subnet_ids
  key_name    = var.key_name
  security_group_ids = module.security_group.security_group_ids

}

# modules/ec2/variables.tf
variable "region" {
  type = string
  description = "AWS Region"
  default = "us-east-1"
}

variable "ami" {
  type = string
  description = "AMI ID"
  default = "ami-0c55b31ad2299a701" # Example AMI ID - Replace with your desired AMI
}

variable "instance_type" {
  type = string
  description = "EC2 Instance Type"
  default = "t2.micro"
}

variable "instance_count" {
  type = number
  description = "Number of EC2 instances"
  default = 2
}

variable "key_name" {
  type = string
  description = "EC2 Key Pair Name"
}

# modules/ec2/outputs.tf
output "instance_ids" {
  value = module.ec2.instance_ids
}


# modules/elb/main.tf
module "elb" {
  source = "./modules/elb"
  region = var.region
  instance_ids = module.ec2.instance_ids
  security_group_ids = module.security_group.security_group_ids
}

# modules/elb/variables.tf
variable "region" {
  type = string
  description = "AWS Region"
  default = "us-east-1"
}

# modules/elb/outputs.tf
output "elb_dns_name" {
  value = module.elb.dns_name
}

# modules/asg/main.tf
module "asg" {
  source = "./modules/asg"
  region = var.region
  instance_ids = module.ec2.instance_ids
  min_size = var.min_size
  max_size = var.max_size
  desired_capacity = var.desired_capacity
  launch_configuration_name = module.launch_config.name

}


# modules/asg/variables.tf
variable "region" {
  type = string
  description = "AWS Region"
  default = "us-east-1"
}

variable "min_size" {
  type = number
  description = "Minimum size of ASG"
  default = 1
}

variable "max_size" {
  type = number
  description = "Maximum size of ASG"
  default = 3
}

variable "desired_capacity" {
  type = number
  description = "Desired capacity of ASG"
  default = 2
}

# modules/asg/outputs.tf
output "asg_name" {
  value = module.asg.name
}


# modules/security_group/main.tf
module "security_group" {
  source = "./modules/security_group"
  region = var.region
  vpc_id = module.vpc.vpc_id
  name = var.name
  description = var.description
  ingress = var.ingress
  egress = var.egress
}

# modules/security_group/variables.tf
variable "region" {
    type = string
    default = "us-east-1"
}
variable "vpc_id" {
    type = string
}
variable "name" {
    type = string
    default = "sharepoint-sg"
}
variable "description" {
    type = string
    default = "Security group for SharePoint application"
}
variable "ingress" {
    type = list(object({
        from_port   = number
        to_port     = number
        protocol    = string
        cidr_blocks = list(string)
    }))
    default = [
        {
            from_port   = 80
            to_port     = 80
            protocol    = "tcp"
            cidr_blocks = ["0.0.0.0/0"]
        },
        {
            from_port   = 443
            to_port     = 443
            protocol    = "tcp"
            cidr_blocks = ["0.0.0.0/0"]
        },
        {
            from_port   = 3306
            to_port     = 3306
            protocol    = "tcp"
            cidr_blocks = ["10.0.0.0/16"] #Allow RDS to communicate
        }
    ]
}
variable "egress" {
  type = list(object({
      from_port   = number
      to_port     = number
      protocol    = string
      cidr_blocks = list(string)
  }))
  default = [
      {
          from_port   = 0
          to_port     = 0
          protocol    = "-1"
          cidr_blocks = ["0.0.0.0/0"]
      }
  ]
}

# modules/security_group/outputs.tf
output "security_group_ids" {
  value = module.security_group.security_group_ids
}

# modules/launch_config/main.tf
module "launch_config" {
  source = "./modules/launch_config"
  region = var.region
  ami = var.ami
  instance_type = var.instance_type
  key_name = var.key_name
  security_group_ids = module.security_group.security_group_ids
}

# modules/launch_config/variables.tf
variable "region" {
  type = string
  description = "AWS Region"
  default = "us-east-1"
}

variable "ami" {
  type = string
  description = "AMI ID"
  default = "ami-0c55b31ad2299a701" # Example AMI ID - Replace with your desired AMI
}

variable "instance_type" {
  type = string
  description = "EC2 Instance Type"
  default = "t2.micro"
}

variable "key_name" {
  type = string
  description = "EC2 Key Pair Name"
}

# modules/launch_config/outputs.tf
output "name" {
  value = module.launch_config.name
}


# main.tf
terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.0"
    }
  }
}

provider "aws" {
  region = "us-east-1"
}

module "vpc" {
  source = "./modules/vpc"
}

module "rds" {
  source = "./modules/rds"
  subnet_ids = module.vpc.subnet_ids
}

module "security_group" {
  source = "./modules/security_group"
  vpc_id = module.vpc.vpc_id
}

module "ec2" {
  source = "./modules/ec2"
  subnet_ids = module.vpc.subnet_ids
  security_group_ids = module.security_group.security_group_ids
  key_name = "your_key_pair_name" # Replace with your key pair name
}

module "elb" {
  source = "./modules/elb"
  instance_ids = module.ec2.instance_ids
  security_group_ids = module.security_group.security_group_ids
}

module "asg" {
  source = "./modules/asg"
  launch_configuration_name = module.launch_config.name
  security_group_ids = module.security_group.security_group_ids

}

module "launch_config" {
  source = "./modules/launch_config"
  security_group_ids = module.security_group.security_group_ids
  key_name = "your_key_pair_name" # Replace with your key pair name
}


# variables.tf
variable "region" {
  type = string
  description = "AWS Region"
  default = "us-east-1"
}

variable "ami" {
  type = string
  description = "AMI ID"
  default = "ami-0c55b31ad2299a701" # Example AMI ID - Replace with your desired AMI
}

variable "instance_type" {
  type = string
  description = "EC2 Instance Type"
  default = "t2.micro"
}

variable "key_name" {
  type = string
  description = "EC2 Key Pair Name"
}

variable "instance_count" {
    type = number
    description = "Number of EC2 instances"
    default = 2
}

variable "min_size" {
    type = number
    description = "Minimum size of ASG"
    default = 1
}

variable "max_size" {
    type = number
    description = "Maximum size of ASG"
    default = 3
}

variable "desired_capacity" {
    type = number
    description = "Desired capacity of ASG"
    default = 2
}

variable "db_name" {
  type = string
  description = "RDS Database Name"
  default = "sharepoint_db"
}

variable "username" {
  type = string
  description = "RDS Username"
  default = "admin"
}

variable "password" {
  type = string
  description = "RDS Password"
  default = "password123" #Please change this in production
}

variable "engine" {
  type = string
  description = "RDS Engine (MySQL or PostgreSQL)"
  default = "mysql"
}

# outputs.tf
output "elb_dns_name" {
  value = module.elb.elb_dns_name
}

output "rds_endpoint" {
  value = module.rds.rds_endpoint
}
```
