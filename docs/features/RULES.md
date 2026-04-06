# Regras Obrigatorias para Implementacao

Leia ANTES de implementar qualquer feature. Violacoes destas regras sao CRITICAL.

## Camadas — O que pode importar o que

```
domain/         → Python puro. ZERO imports de libs externas.
application/    → Apenas interfaces do domain/. ZERO imports de libs externas.
infrastructure/ → Implementa interfaces. UNICA camada que importa libs (SQLAlchemy, bcrypt, jose, boto3).
container.py    → Conecta interfaces → implementacoes. UNICO arquivo que importa de infrastructure/.
presentation/   → Usa container. Delega aos use cases.
```

**PROIBIDO em domain/ e application/:**
- `import bcrypt`
- `from jose import jwt`
- `import boto3`
- `from sqlalchemy import ...`
- `from fastapi import ...`
- Qualquer import de lib externa

## Servicos Externos

Se um use case precisa de hash, JWT, email, HTTP, fila:
1. Criar **interface ABC** em `domain/services/nome_servico.py`
2. Criar **implementacao** em `infrastructure/services/nome_concreto.py`
3. Registrar como `providers.Singleton` no `container.py`
4. Injetar no use case via construtor

## Entidades e Agregados

- Toda entidade DEVE ter `__post_init__` validando campos obrigatorios
- NUNCA defaults vazios sem validacao (`str = ""` sem check)
- Regras de negocio DENTRO do agregado (ex: `saldo >= 0`)
- Value Objects: `@dataclass(frozen=True)` — imutaveis

## Container (dependency-injector)

- `providers.Singleton` para repos e servicos (stateless, reutilizaveis)
- `providers.Factory` para use cases (stateless por chamada)
- `wiring_config` no container (nao `wire()` manual no app.py)
- Testes: `container.provider.override()` com fakes

## Testes

- Testes de integracao via TestClient (monolito) ou handler direto (Lambda)
- Cada feature deve ter >= 70% cobertura no modulo
- `radon cc` sem funcao acima de B
