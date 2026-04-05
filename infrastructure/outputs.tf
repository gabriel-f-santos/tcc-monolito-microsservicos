output "alb_dns" {
  description = "DNS do Application Load Balancer"
  value       = module.compute.alb_dns
}

output "rds_endpoint" {
  description = "Endpoint do RDS PostgreSQL"
  value       = module.database.endpoint
}

output "ecr_repo_url" {
  description = "URL do repositorio ECR"
  value       = module.iam.ecr_repo_url
}

output "asg_name" {
  description = "Nome do Auto Scaling Group"
  value       = module.compute.asg_name
}
