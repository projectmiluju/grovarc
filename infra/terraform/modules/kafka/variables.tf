variable "project" { type = string }
variable "environment" { type = string }
variable "vpc_id" { type = string }
variable "private_subnets" { type = list(string) }
variable "instance_type" { type = string }
variable "kafka_version" { type = string }
