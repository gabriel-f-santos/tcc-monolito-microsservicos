variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Nome do projeto (usado como prefixo)"
  type        = string
  default     = "tcc-monolito"
}

variable "environment" {
  description = "Ambiente (dev, prod)"
  type        = string
  default     = "dev"
}

variable "db_password" {
  description = "Senha do banco RDS"
  type        = string
  sensitive   = true
}

variable "my_ip" {
  description = "Seu IP para acesso SSH (formato CIDR: x.x.x.x/32)"
  type        = string
}
