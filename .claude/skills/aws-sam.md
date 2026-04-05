---
name: aws-sam
description: Use when creating or editing AWS SAM templates (template.yaml), Lambda handlers, API Gateway config, DynamoDB tables, SNS/SQS resources, or any serverless infrastructure for this project.
---

# AWS SAM Reference

## Overview

AWS SAM (Serverless Application Model) templates for this project define Lambda functions, API Gateway, DynamoDB tables, and SNS/SQS messaging.

## Template Structure

```yaml
AWSTemplateFormatVersion: '2010-09-09'
Transform: AWS::Serverless-2016-10-31
Description: Service description

Globals:
  Function:
    Runtime: python3.13
    MemorySize: 1024
    Timeout: 30
    Tracing: Active
    Environment:
      Variables:
        ENVIRONMENT: !Ref Environment

Parameters:
  Environment:
    Type: String
    Default: dev

Resources:
  # Functions, tables, topics, queues...

Outputs:
  ApiUrl:
    Value: !Sub "https://${ServerlessRestApi}.execute-api.${AWS::Region}.amazonaws.com/Prod"
```

## Lambda Handler Pattern (No Mangum)

```python
import json

def handler(event, context):
    """Raw Lambda handler — no FastAPI, no Mangum."""
    http_method = event["httpMethod"]
    path = event.get("pathParameters") or {}
    body = json.loads(event.get("body") or "{}")

    # Delegate to use case
    result = use_case.execute(...)

    return {
        "statusCode": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps(result)
    }
```

## Resource Quick Reference

| Resource | Type | Key Properties |
|----------|------|----------------|
| Lambda | `AWS::Serverless::Function` | Handler, CodeUri, Events (Api) |
| DynamoDB | `AWS::DynamoDB::Table` | KeySchema, AttributeDefinitions, BillingMode: PAY_PER_REQUEST |
| SNS Topic | `AWS::SNS::Topic` | TopicName |
| SQS Queue | `AWS::SQS::Queue` | QueueName, VisibilityTimeout |
| SNS→SQS Sub | `AWS::SNS::Subscription` | Protocol: sqs, Endpoint: !GetAtt Queue.Arn |
| Lambda→SQS | `AWS::Serverless::Function` Events | `Type: SQS, Properties: Queue: !GetAtt Queue.Arn` |

## API Gateway Events

```yaml
MyFunction:
  Type: AWS::Serverless::Function
  Properties:
    Handler: src/presentation/handlers/product.handler
    CodeUri: .
    Events:
      GetHealth:
        Type: Api
        Properties:
          Path: /health
          Method: get
      CreateProduct:
        Type: Api
        Properties:
          Path: /api/v1/produtos
          Method: post
```

## DynamoDB Table

```yaml
ProdutosTable:
  Type: AWS::DynamoDB::Table
  Properties:
    TableName: !Sub "${Environment}-produtos"
    BillingMode: PAY_PER_REQUEST
    AttributeDefinitions:
      - AttributeName: id
        AttributeType: S
    KeySchema:
      - AttributeName: id
        KeyType: HASH
```

## Project Conventions

- Handler files in `src/presentation/handlers/`
- One handler file per bounded context
- Handlers parse event → call use case → format response
- Use `PAY_PER_REQUEST` billing (no provisioned capacity)
- Memory: 1024MB (avoids severe cold starts)
- Tracing: Active (X-Ray)
- Environment variable for table names (no hardcoded)
