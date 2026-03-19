terraform {
  required_version = ">= 1.7"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  backend "s3" {
    bucket         = "grovarc-tfstate-dev"
    key            = "dev/terraform.tfstate"
    region         = "ap-northeast-2"
    dynamodb_table = "grovarc-tfstate-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "grovarc"
      Environment = "dev"
      ManagedBy   = "terraform"
    }
  }
}

# ── VPC ───────────────────────────────────────────────────────────────────────
module "vpc" {
  source = "../../modules/vpc"

  project     = var.project
  environment = var.environment
  vpc_cidr    = "10.0.0.0/16"
}

# ── EKS ───────────────────────────────────────────────────────────────────────
module "eks" {
  source = "../../modules/eks"

  project          = var.project
  environment      = var.environment
  vpc_id           = module.vpc.vpc_id
  private_subnets  = module.vpc.private_subnet_ids
  cluster_version  = "1.30"
  node_instance_type = "t3.medium"
  node_desired_size  = 2
  node_min_size      = 1
  node_max_size      = 3
}

# ── RDS (PostgreSQL + pgvector) ───────────────────────────────────────────────
module "rds" {
  source = "../../modules/rds"

  project         = var.project
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnet_ids
  instance_class  = "db.t3.micro"
  db_name         = "grovarc"
  db_username     = var.db_username
  db_password     = var.db_password
}

# ── ElastiCache (Redis) ───────────────────────────────────────────────────────
module "redis" {
  source = "../../modules/redis"

  project         = var.project
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnet_ids
  node_type       = "cache.t3.micro"
}

# ── MSK (Kafka) ───────────────────────────────────────────────────────────────
module "kafka" {
  source = "../../modules/kafka"

  project         = var.project
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnet_ids
  instance_type   = "kafka.t3.small"
  kafka_version   = "3.6.0"
}

# ── DocumentDB (MongoDB 호환) ─────────────────────────────────────────────────
module "mongodb" {
  source = "../../modules/mongodb"

  project         = var.project
  environment     = var.environment
  vpc_id          = module.vpc.vpc_id
  private_subnets = module.vpc.private_subnet_ids
  instance_class  = "db.t3.medium"
  db_username     = var.mongo_username
  db_password     = var.mongo_password
}

# ── S3 (정적 파일 & 로그) ─────────────────────────────────────────────────────
module "s3" {
  source = "../../modules/s3"

  project     = var.project
  environment = var.environment
}
