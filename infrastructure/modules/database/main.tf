variable "project_name" { type = string }
variable "db_password" {
  type      = string
  sensitive = true
}
variable "vpc_id" { type = string }
variable "private_subnet_ids" { type = list(string) }
variable "ec2_sg_id" { type = string }

# ============================================================
# RDS SECURITY GROUP
# ============================================================

resource "aws_security_group" "rds" {
  name   = "${var.project_name}-rds-sg"
  vpc_id = var.vpc_id

  ingress {
    description     = "PostgreSQL from EC2"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [var.ec2_sg_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = { Name = "${var.project_name}-rds-sg" }
}

# ============================================================
# DB SUBNET GROUP
# ============================================================

resource "aws_db_subnet_group" "main" {
  name       = "${var.project_name}-db-subnet"
  subnet_ids = var.private_subnet_ids

  tags = { Name = "${var.project_name}-db-subnet" }
}

# ============================================================
# RDS INSTANCE
# ============================================================

resource "aws_db_instance" "postgres" {
  identifier     = "${var.project_name}-postgres"
  engine         = "postgres"
  engine_version = "16"
  instance_class = "db.t4g.micro"

  allocated_storage = 20
  storage_type      = "gp3"

  db_name  = "monolito"
  username = "monolito_admin"
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  publicly_accessible    = false

  backup_retention_period = 1
  skip_final_snapshot     = true

  tags = { Name = "${var.project_name}-postgres" }

  lifecycle {
    ignore_changes = [password]
  }
}

# ============================================================
# OUTPUTS
# ============================================================

output "endpoint" { value = aws_db_instance.postgres.endpoint }

output "connection_url" {
  value     = "postgresql://monolito_admin:${var.db_password}@${aws_db_instance.postgres.endpoint}/monolito"
  sensitive = true
}
