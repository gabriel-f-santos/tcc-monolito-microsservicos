# Microsservicos MVC — Grupo de Controle

## IMPORTANTE

Estes microsservicos sao a migracao do `monolito-mvc/` (sem DDD).
Servem para comparar com `microsservicos/` (migrado do DDD).

## Arquitetura (simples — sem DDD)

Cada servico e um Lambda handler com queries DynamoDB diretas:

```
xxx-service/
├── src/
│   └── handlers/
│       ├── health.py
│       └── xxx.py      # Handler com queries boto3 inline
├── tests/
├── pyproject.toml
└── requirements.txt
```

**SEM:** domain/, application/, infrastructure/, container.py, interfaces ABC, Value Objects, dependency-injector.

## Regras

- Handlers fazem queries DynamoDB diretamente (boto3 inline)
- Validacao inline nos handlers
- bcrypt/jose importados diretamente
- Sem camadas, sem separacao de responsabilidades
- Mesma API e comportamento do monolito-mvc e do monolito DDD

## Cada servico e independente

- Proprio pyproject.toml e requirements.txt
- Proprios tests/
- Rodar testes: `cd xxx-service && pytest`
