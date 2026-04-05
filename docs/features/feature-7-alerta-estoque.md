# Feature 7: Relatorio de Estoque Baixo (Feature Nova — Medicao Principal)

## Contexto

Leia estes arquivos antes de implementar:
- `docs/architecture.md` — padrao DDD, camadas, container DI (dependency-injector)
- `monolito/CLAUDE.md` ou `microsservicos/CLAUDE.md` — regras do projeto
- `docs/spec.md` secoes 1-7 — dominio, agregados, VOs, erros

Pre-requisito: Features 0-4 ja implementadas (monolito) ou Features 0-5 (microsservicos).

**IMPORTANTE:** Esta feature e a medicao principal do TCC. Ela sera implementada em ambas as arquiteturas (monolito e microsservicos) ja funcionais, para medir o tempo de adicionar uma feature nova em cada uma. O cronometro comeca no prompt.

## O que implementar

Endpoint que retorna itens de estoque com saldo abaixo de um threshold, para alertar sobre produtos que precisam de reposicao.

## Endpoint

| Metodo | Endpoint | Query Params | Response |
|--------|----------|-------------|----------|
| GET | `/api/v1/estoque/alertas` | `?saldo_max=10&page=1&size=20` | `200` + Lista paginada de itens com saldo <= saldo_max |

## Regras de negocio

1. `saldo_max` e obrigatorio (query param)
2. Retorna apenas itens ativos com `saldo <= saldo_max`
3. Ordenado por saldo crescente (mais critico primeiro)
4. Itens inativos nao aparecem no alerta
5. Se nao ha itens abaixo do threshold, retorna lista vazia

## Response Schema

```json
{
  "alertas": [
    {
      "id": "uuid",
      "produto_id": "uuid",
      "sku": "ELET-001",
      "nome_produto": "Teclado Mecanico",
      "categoria_nome": "Eletronicos",
      "saldo": 3,
      "ativo": true
    }
  ],
  "total": 2,
  "saldo_max": 10,
  "page": 1,
  "size": 20
}
```

## Diferenca entre arquiteturas

| Aspecto | Monolito | Microsservicos |
|---------|----------|----------------|
| Query | SQL `WHERE saldo <= ? AND ativo = true ORDER BY saldo` | DynamoDB Scan com FilterExpression |
| Complexidade | Simples (SQL nativo) | Mais complexa (Scan e ineficiente, pode precisar de GSI) |
| Performance | Rapido (indice SQL) | Depende do tamanho da tabela |

**Ponto pro artigo:** esta diferenca mostra o trade-off real entre SQL (queries flexiveis) e DynamoDB (precisa planejar access patterns antecipadamente).

## Testes esperados (3)

```
test_alertas_retorna_itens_com_saldo_baixo
  Criar 3 produtos + entradas (saldo 5, 15, 3)
  GET /api/v1/estoque/alertas?saldo_max=10 → 200
  Retorna 2 itens (saldo 3 e 5), ordenados por saldo

test_alertas_sem_itens_abaixo
  Criar produto + entrada saldo=100
  GET /api/v1/estoque/alertas?saldo_max=10 → 200, lista vazia

test_alertas_ignora_inativos
  Criar produto + entrada saldo=5 + desativar produto
  GET /api/v1/estoque/alertas?saldo_max=10 → 200, lista vazia
```

## Arquivos a modificar (monolito)

```
src/estoque/
├── domain/repositories/item_estoque_repository.py  # Adicionar metodo listar_por_saldo_max
├── infrastructure/repositories/
│   └── sqlalchemy_item_estoque_repository.py       # Implementar query SQL
├── application/use_cases/
│   └── listar_alertas.py                           # NOVO
├── container.py                                    # Adicionar provider
└── presentation/
    ├── routes.py                                   # Adicionar rota GET /alertas
    └── schemas.py                                  # Schema de response
```

## Criterio de pronto

- [ ] 3 testes passam
- [ ] `radon cc src/estoque/ -s -a` sem funcao acima de B
- [ ] Endpoint protegido por JWT
- [ ] Ordenado por saldo crescente
