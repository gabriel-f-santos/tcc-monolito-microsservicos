---
name: aws-sam
description: Use when creating, editing, or debugging AWS SAM templates, Lambda handlers, API Gateway config, DynamoDB tables, SNS/SQS, IAM policies, or deploying serverless infrastructure. Covers common pitfalls from production experience.
---

# AWS SAM — Guia Completo para Deploy Serverless

## Overview

AWS SAM (Serverless Application Model) para microsservicos Python com Lambda, API Gateway, DynamoDB, SNS/SQS. Inclui licoes aprendidas de erros reais em producao.

## Estrutura de Projeto (Independente por Servico)

```
microsservicos/
├── template.yaml              # SAM template (orquestra tudo)
├── auth-service/
│   ├── pyproject.toml         # deps do servico
│   ├── requirements.txt       # OBRIGATORIO para SAM build
│   ├── src/
│   │   ├── domain/
│   │   ├── application/
│   │   ├── infrastructure/
│   │   ├── presentation/handlers/
│   │   └── container.py
│   └── tests/
├── catalogo-service/
│   ├── pyproject.toml
│   ├── requirements.txt
│   ├── src/
│   └── tests/
└── estoque-service/
    ├── pyproject.toml
    ├── requirements.txt
    ├── src/
    └── tests/
```

**CRITICO: Cada servico DEVE ter `requirements.txt`** — SAM build usa ele para instalar deps no pacote Lambda. Sem ele, Lambda falha com `ModuleNotFoundError`.

## Template.yaml — Estrutura Base

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31

Globals:
  Function:
    Runtime: python3.13
    MemorySize: 512
    Timeout: 30
    Tracing: Active
    # NAO colocar Policies em Globals — causa InvalidSamDocumentException
```

## IAM Policies — OBRIGATORIO em Cada Funcao

**Globals NAO suporta Policies.** Adicionar em CADA funcao que acessa DynamoDB/SNS:

```yaml
  MinhaFunction:
    Type: AWS::Serverless::Function
    Properties:
      Handler: src/presentation/handlers/meu_handler.handler
      CodeUri: meu-service
      Policies:
        - Version: "2012-10-17"
          Statement:
            - Effect: Allow
              Action:
                - dynamodb:GetItem
                - dynamodb:PutItem
                - dynamodb:UpdateItem
                - dynamodb:DeleteItem
                - dynamodb:Scan
                - dynamodb:Query
              Resource: !Sub "arn:aws:dynamodb:${AWS::Region}:${AWS::AccountId}:table/tcc-*"
            - Effect: Allow
              Action:
                - sns:Publish
              Resource: !Sub "arn:aws:sns:${AWS::Region}:${AWS::AccountId}:tcc-*"
```

**Funcoes que NAO precisam de policy:** health checks (nao acessam banco/fila).

## Lambda Authorizer — Pitfalls

### Cache com Wildcard ARN (CRITICO)

O API Gateway cacheia a policy do authorizer por token (TTL configuravel). Se a policy retorna o `methodArn` especifico, o cache so funciona pra AQUELA rota. Requests para outras rotas com o mesmo token recebem 403.

```python
# ERRADO — policy especifica para uma rota, cache invalida outras
return _generate_policy(user_id, "Allow", event["methodArn"])

# CORRETO — wildcard permite todas as rotas da API
arn_parts = event["methodArn"].split(":")
region = arn_parts[3]
account_id = arn_parts[4]
api_gw_parts = arn_parts[5].split("/")
api_id = api_gw_parts[0]
stage = api_gw_parts[1]
wildcard_arn = f"arn:aws:execute-api:{region}:{account_id}:{api_id}/{stage}/*"
return _generate_policy(user_id, "Allow", wildcard_arn)
```

### Configuracao no Template

```yaml
  TccApi:
    Type: AWS::Serverless::Api
    Properties:
      StageName: Prod
      Auth:
        DefaultAuthorizer: JwtAuthorizer
        Authorizers:
          JwtAuthorizer:
            FunctionArn: !GetAtt AuthorizerFunction.Arn
            Identity:
              Header: Authorization
              ReauthorizeEvery: 300  # Cache 5 min

  # Rotas publicas (sem auth):
  AuthRegistrarFunction:
    Events:
      Api:
        Properties:
          Auth:
            Authorizer: NONE  # Publico
```

## Lambda Handler — Roteamento por Path

Lambda recebe o `path` do API Gateway como esta no template. Se o template define `/api/v1/categorias`, o handler recebe exatamente `/api/v1/categorias`.

```python
def handler(event, context):
    method = event["httpMethod"]
    path = event.get("path", "")

    # CORRETO — path exatamente como no template.yaml
    if path == "/api/v1/categorias" and method == "POST":
        return _criar_categoria(event)

    # ERRADO — path diferente do template
    if path == "/catalogo/categorias":  # NAO! template diz /api/v1/categorias
```

**Regra:** o path no handler DEVE corresponder exatamente ao `Path:` no template.yaml.

## DynamoDB Repos — endpoint_url

Repos podem aceitar `endpoint_url` para testes locais (DynamoDB Local), mas o container NAO deve ter `providers.Dependency()` para endpoint_url. Use default no construtor do repo:

```python
# CORRETO — endpoint_url opcional com default None
class DynamoDBRepo:
    def __init__(self, table_name: str, endpoint_url: str | None = None):
        kwargs = {"region_name": "us-east-1"}
        if endpoint_url:
            kwargs["endpoint_url"] = endpoint_url
        self.table = boto3.resource("dynamodb", **kwargs).Table(table_name)

# CORRETO — container NAO passa endpoint_url
class MeuContainer(DeclarativeContainer):
    table_name = providers.Dependency(instance_of=str)
    # SEM endpoint_url aqui
    repo = providers.Singleton(DynamoDBRepo, table_name=table_name)
```

## Deploy — Passo a Passo

### Primeiro Deploy

```bash
# 1. Criar S3 bucket para artifacts
aws s3 mb s3://meu-sam-artifacts-ACCOUNT_ID

# 2. Build (usar --use-container se Python local != 3.13)
cd microsservicos
sam build --use-container

# 3. Deploy
sam deploy \
  --stack-name meu-stack \
  --no-confirm-changeset \
  --s3-bucket meu-sam-artifacts-ACCOUNT_ID \
  --capabilities CAPABILITY_IAM

# 4. Pegar URL da API
aws cloudformation describe-stacks --stack-name meu-stack \
  --query 'Stacks[0].Outputs[?OutputKey==`ApiUrl`].OutputValue' --output text
```

### Deploys Subsequentes

```bash
rm -rf .aws-sam  # Forcar rebuild limpo
sam build --use-container
sam deploy --stack-name meu-stack --no-confirm-changeset \
  --s3-bucket meu-sam-artifacts-ACCOUNT_ID --capabilities CAPABILITY_IAM
```

**IMPORTANTE:** `sam deploy` detecta mudancas no template.yaml mas nem sempre no codigo Python. Sempre rodar `rm -rf .aws-sam && sam build` antes.

### GitHub Actions

```yaml
- name: SAM build
  working-directory: microsservicos
  run: sam build

- name: SAM deploy
  working-directory: microsservicos
  run: |
    sam deploy \
      --stack-name $STACK_NAME \
      --no-confirm-changeset \
      --no-fail-on-empty-changeset \
      --s3-bucket $S3_BUCKET \
      --capabilities CAPABILITY_IAM
```

## Checklist — Antes de Deploy

- [ ] Cada servico tem `requirements.txt` com TODAS as deps (nao so pyproject.toml)
- [ ] Cada Lambda que acessa DynamoDB tem `Policies` com DynamoDB actions
- [ ] Cada Lambda que publica SNS tem `Policies` com sns:Publish
- [ ] Lambda Authorizer retorna wildcard ARN (nao methodArn especifico)
- [ ] Rotas publicas tem `Auth: Authorizer: NONE`
- [ ] Health checks NAO exigem auth
- [ ] Paths no handler correspondem EXATAMENTE aos `Path:` no template.yaml
- [ ] Container NAO tem `endpoint_url` como `providers.Dependency()` obrigatorio
- [ ] `sam build --use-container` se Python local != runtime da Lambda
- [ ] `rm -rf .aws-sam` antes de rebuild para garantir codigo atualizado

## Erros Comuns e Solucoes

| Erro | Causa | Solucao |
|------|-------|---------|
| `ModuleNotFoundError: dependency_injector` | Falta requirements.txt | Criar requirements.txt no servico |
| `InvalidSamDocumentException` | Policies em Globals | Mover Policies para cada funcao |
| `AccessDeniedException: dynamodb:Scan` | Sem IAM policy | Adicionar Policies na funcao |
| 403 em rotas com token valido | Authorizer retorna ARN especifico | Usar wildcard ARN |
| `ROTA_NAO_ENCONTRADA` no handler | Path errado no handler | Alinhar com template.yaml |
| `Dependency "X" is not defined` | Container tem Dependency nao passada | Remover ou dar default |
| `No changes to deploy` | SAM cache | `rm -rf .aws-sam && sam build` |
| `Binary validation failed for python` | Python local != runtime | `sam build --use-container` |
