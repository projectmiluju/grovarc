variable "aws_region" {
  description = "AWS 리전"
  type        = string
  default     = "ap-northeast-2"
}

variable "project" {
  description = "프로젝트명"
  type        = string
  default     = "grovarc"
}

variable "environment" {
  description = "환경 (dev / prod)"
  type        = string
  default     = "dev"
}

variable "db_username" {
  description = "RDS PostgreSQL 유저명"
  type        = string
  sensitive   = true
}

variable "db_password" {
  description = "RDS PostgreSQL 비밀번호"
  type        = string
  sensitive   = true
}

variable "mongo_username" {
  description = "DocumentDB 유저명"
  type        = string
  sensitive   = true
}

variable "mongo_password" {
  description = "DocumentDB 비밀번호"
  type        = string
  sensitive   = true
}
