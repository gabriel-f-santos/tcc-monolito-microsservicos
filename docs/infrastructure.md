# Especificacao de Infraestrutura

## Visao Geral

Duas infraestruturas independentes para comparacao no TCC:

| Dimensao | Monolito | Microsservicos |
|----------|----------|----------------|
| Computacao | EC2 (ASG) + ALB | AWS Lambda + API Gateway |
| Banco | RDS PostgreSQL 16 | DynamoDB (PAY_PER_REQUEST) |
| Mensageria | In-process (sync) | SNS + SQS |
| IaC | Terraform | AWS SAM (CloudFormation) |
| Deploy | Docker image → ECR → Instance Refresh | sam build → sam deploy |
| Custo estimado | ~$38/mes (fixo) | ~$5/mes (pay-per-use) |

---

## Monolito — Terraform

### Arquitetura

```
Internet → ALB (HTTPS:443) → Target Group (:8080) → ASG (1-2 EC2 t3.micro) → RDS PostgreSQL
```

### Modulos

#### 1. Network (VPC)

| Recurso | Configuracao |
|---------|-------------|
| VPC | CIDR 10.0.0.0/16 |
| Public Subnets | 10.0.1.0/24, 10.0.2.0/24 (2 AZs) |
| Private Subnets | 10.0.3.0/24, 10.0.4.0/24 (2 AZs, para RDS) |
| Internet Gateway | Rota 0.0.0.0/0 nas subnets publicas |
| NAT Gateway | Nenhum (EC2 em subnet publica, RDS em privada) |

**Decisao:** Sem NAT Gateway para reduzir custo. EC2 fica em subnet publica com Security Group restritivo. RDS fica em subnet privada acessivel apenas pelo EC2.

#### 2. Compute (EC2 + ASG + ALB)

**Application Load Balancer:**

| Configuracao | Valor |
|-------------|-------|
| Tipo | Application (Layer 7) |
| Subnets | 2 publicas (multi-AZ) |
| Listener HTTP (80) | Redirect → HTTPS |
| Listener HTTPS (443) | Forward → Target Group |
| Certificado | ACM (DNS validation) |
| Security Group | Ingress 80/443 de 0.0.0.0/0 |

**Target Group:**

| Configuracao | Valor |
|-------------|-------|
| Porta | 8080 |
| Protocolo | HTTP |
| Health check | GET /health |
| Intervalo | 10s |
| Threshold healthy | 2 |
| Threshold unhealthy | 3 |

**Auto Scaling Group:**

| Configuracao | Valor |
|-------------|-------|
| Min | 1 |
| Max | 2 |
| Desired | 1 |
| Health check type | ELB |
| Grace period | 300s |

**Scaling Policies:**

| Politica | Metrica | Target |
|----------|---------|--------|
| CPU | ASGAverageCPUUtilization | 60% |

**Launch Template:**

| Configuracao | Valor |
|-------------|-------|
| Instance type | t3.micro |
| AMI | Amazon Linux 2023 (latest) |
| EBS | 20GB gp3 |
| User data | Pull Docker image do ECR, run na porta 8080 |
| IAM Role | ECR read + CloudWatch logs |

**User Data Script (resumo):**
1. Instalar Docker
2. Login no ECR
3. Pull imagem `tcc-monolito:latest`
4. Run container na porta 8080 com `DATABASE_URL` via env var
5. Configurar CloudWatch agent para metricas de memoria

#### 3. Database (RDS)

| Configuracao | Valor |
|-------------|-------|
| Engine | PostgreSQL 16 |
| Instance class | db.t3.micro |
| Storage | 20GB gp3 |
| Multi-AZ | Nao (custo) |
| Public access | Nao |
| Subnets | 2 privadas |
| Security Group | Ingress 5432 apenas do EC2 SG |
| Backup retention | 1 dia |
| Skip final snapshot | Sim (ambiente de teste) |

#### 4. IAM

**EC2 Instance Role:**
- `AmazonEC2ContainerRegistryReadOnly` — pull imagens do ECR
- `CloudWatchAgentServerPolicy` — enviar metricas
- Policy customizada: escrever em CloudWatch Logs `/tcc/*`

**GitHub Actions User:**
- `ecr:GetAuthorizationToken`
- `ecr:BatchCheckLayerAvailability`, `PutImage`, `InitiateLayerUpload`, `UploadLayerPart`, `CompleteLayerUpload`
- `autoscaling:StartInstanceRefresh`, `DescribeInstanceRefreshes`

#### 5. ECR

| Configuracao | Valor |
|-------------|-------|
| Repository | tcc-monolito |
| Image tag mutability | MUTABLE (latest) |
| Lifecycle | Manter ultimas 5 imagens |

#### 6. Security Groups

| SG | Ingress | Source |
|----|---------|--------|
| ALB SG | 80, 443 | 0.0.0.0/0 |
| EC2 SG | 8080 | ALB SG |
| EC2 SG | 22 | Meu IP (variavel) |
| RDS SG | 5432 | EC2 SG |

---

## Microsservicos — AWS SAM

### Arquitetura

```
Internet → API Gateway → Lambda Handlers → DynamoDB
                                         → SNS → SQS → Lambda Consumer
```

### Recursos (template.yaml)

**Funcoes Lambda:**

| Funcao | Handler | Trigger | Env Vars |
|--------|---------|---------|----------|
| CatalogoHealth | catalogo-service/.../health.handler | API GET /catalogo/health | PRODUTOS_TABLE, CATEGORIAS_TABLE, EVENTOS_TOPIC_ARN |
| EstoqueHealth | estoque-service/.../health.handler | API GET /estoque/health | ITENS_ESTOQUE_TABLE, MOVIMENTACOES_TABLE |
| EstoqueEventConsumer | estoque-service/.../event_consumer.handler | SQS | ITENS_ESTOQUE_TABLE |

**Config Lambda (Globals):**

| Configuracao | Valor |
|-------------|-------|
| Runtime | python3.13 |
| Memory | 512 MB |
| Timeout | 30s |
| Tracing | Active (X-Ray) |

**DynamoDB Tables:**

| Tabela | Partition Key | Billing |
|--------|--------------|---------|
| {env}-produtos | id (S) | PAY_PER_REQUEST |
| {env}-categorias | id (S) | PAY_PER_REQUEST |
| {env}-itens-estoque | id (S) | PAY_PER_REQUEST |
| {env}-movimentacoes | id (S) | PAY_PER_REQUEST |

**Mensageria:**

| Recurso | Tipo | Configuracao |
|---------|------|-------------|
| EventosDominioTopic | SNS Topic | Topico unico para todos os eventos |
| EstoqueEventosQueue | SQS Queue | VisibilityTimeout 60s |
| Subscription | SNS → SQS | Estoque consome todos os eventos do Catalogo |
| Queue Policy | SQS Policy | Permite SNS enviar para a fila |

---

## CI/CD — GitHub Actions

### Pipeline do Monolito

```
Push main → Build Docker → Push ECR → Instance Refresh ASG
```

**Etapas:**
1. Checkout
2. Setup Python 3.13
3. Instalar dependencias
4. Rodar testes (`pytest`)
5. Rodar analise estatica (`radon cc`, `radon mi`, `xenon`)
6. Salvar relatorios como artefatos
7. Build Docker image
8. Login ECR + push image
9. Trigger Instance Refresh no ASG (rolling deploy)

### Pipeline dos Microsservicos

```
Push main → sam build → sam deploy
```

**Etapas:**
1. Checkout
2. Setup Python 3.13
3. Instalar dependencias dos testes
4. Rodar testes (`pytest`)
5. Rodar analise estatica (`radon cc`, `radon mi`)
6. Salvar relatorios como artefatos
7. Setup SAM CLI
8. `sam build`
9. `sam deploy --no-confirm-changeset --stack-name tcc-microsservicos-{env}`

### Secrets necessarios no GitHub

| Secret | Usado em |
|--------|----------|
| AWS_ACCESS_KEY_ID | Ambos |
| AWS_SECRET_ACCESS_KEY | Ambos |
| AWS_REGION | Ambos |
| ECR_REPOSITORY | Monolito |
| ASG_NAME | Monolito |
| SAM_S3_BUCKET | Microsservicos |

---

## Estimativa de Custo Mensal (us-east-1)

### Monolito

| Recurso | Custo/mes |
|---------|-----------|
| EC2 t3.micro (1 instancia, on-demand) | $8.50 |
| RDS db.t3.micro (single-AZ) | $13.00 |
| ALB (fixo + LCU) | $16.50 |
| ECR (armazenamento) | $0.50 |
| CloudWatch Logs | $1.00 |
| **Total** | **~$39.50** |

### Microsservicos

| Recurso | Custo/mes (carga baixa) |
|---------|------------------------|
| Lambda (100k invocacoes) | $0.20 |
| API Gateway (100k requests) | $0.35 |
| DynamoDB (on-demand, 100k R+W) | $1.25 |
| SNS + SQS | $0.10 |
| X-Ray | $0.50 |
| **Total** | **~$2.40** |

### Comparacao para o artigo

| Cenario | Monolito | Microsservicos | Mais barato |
|---------|----------|----------------|-------------|
| Carga baixa (100 req/dia) | $39.50 | $2.40 | Serverless |
| Carga media (10k req/dia) | $39.50 | $8.00 | Serverless |
| Carga alta (100k req/dia) | $39.50* | $45.00 | Monolito |
| Carga constante 24/7 | $39.50 | $120.00+ | Monolito |

*Monolito pode precisar escalar para 2 instancias em carga alta (~$48)

**Insight para o TCC:** Serverless e mais barato ate ~50k req/dia. Acima disso, o custo fixo do monolito se torna vantajoso. Essa e exatamente a discussao critica que o professor pediu.

---

## Diferencas em relacao ao Nubo

| Aspecto | Nubo (producao) | TCC (estudo) | Justificativa |
|---------|-----------------|--------------|---------------|
| Instance type | t3.small | t3.micro | Custo minimo |
| ASG max | 10 | 2 | Escopo de teste |
| RDS | db.t3.small | db.t3.micro | Custo minimo |
| AMI | Custom hardened (Packer) | Amazon Linux 2023 | Simplicidade |
| Redis | Sim (t3.micro) | Nao | Fora do escopo |
| Metabase | Sim | Nao | Fora do escopo |
| Cloudflare | Sim | Nao | Acesso direto ao ALB |
| Scheduled scaling | Sim (horario de aula) | Nao | Carga de teste apenas |
| Monitoring | CloudWatch dashboard | Grafana Cloud | Requisito do TCC |
