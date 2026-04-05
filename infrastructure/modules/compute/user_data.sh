#!/bin/bash
set -euxo pipefail

# Install Docker
dnf install -y docker
systemctl enable docker
systemctl start docker

# Configure Docker log rotation
cat > /etc/docker/daemon.json <<'DOCKER_EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
DOCKER_EOF
systemctl restart docker

# Login to ECR
aws ecr get-login-password --region ${aws_region} | docker login --username AWS --password-stdin ${ecr_repo_url}

# Pull and run application
docker pull ${ecr_repo_url}:latest

docker run -d \
  --name monolito \
  --restart always \
  --memory=512m \
  --memory-swap=512m \
  -p 8080:8080 \
  -e DATABASE_URL="${database_url}" \
  -e OTEL_ENABLED="${otel_enabled}" \
  -e OTEL_EXPORTER_OTLP_ENDPOINT="${otel_endpoint}" \
  -e OTEL_EXPORTER_OTLP_HEADERS="${otel_headers}" \
  ${ecr_repo_url}:latest
