output "vpc_id" {
  description = "VPC ID"
  value       = module.vpc.vpc_id
}

output "eks_cluster_endpoint" {
  description = "EKS 클러스터 엔드포인트"
  value       = module.eks.cluster_endpoint
  sensitive   = true
}

output "rds_endpoint" {
  description = "RDS 엔드포인트"
  value       = module.rds.endpoint
  sensitive   = true
}

output "redis_endpoint" {
  description = "Redis 엔드포인트"
  value       = module.redis.endpoint
  sensitive   = true
}

output "kafka_bootstrap_brokers" {
  description = "Kafka 브로커 주소"
  value       = module.kafka.bootstrap_brokers
  sensitive   = true
}

output "mongodb_endpoint" {
  description = "DocumentDB 엔드포인트"
  value       = module.mongodb.endpoint
  sensitive   = true
}
