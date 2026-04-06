# Feature 4: Saida de Estoque

## Contexto

Leia estes arquivos antes de implementar:
- `docs/features/RULES.md` — regras obrigatorias (violacoes sao CRITICAL)
- `docs/architecture.md` — padrao DDD, camadas, container DI (dependency-injector)
- `monolito/CLAUDE.md` ou `microsservicos/CLAUDE.md` — regras do projeto
- `docs/spec.md` secoes 1-7 — dominio, agregados, VOs, erros

Pre-requisito: Features 0-3 ja implementadas. Itens de estoque existem com saldo.

## O que implementar

Adicionar registro de saida de estoque ao modulo `src/estoque/` (monolito) ou `estoque-service/` (microsservicos). A **invariante principal** e que o saldo nunca pode ser negativo — essa validacao deve estar dentro do agregado ItemEstoque, nao no use case.

## Endpoint

| Metodo | Endpoint | Request Body | Response |
|--------|----------|-------------|----------|
| POST | `/api/v1/estoque/{id}/saida` | `{ "quantidade": 30, "motivo": "Venda" }` | `201` + Movimentacao |

## Regras de negocio

1. Quantidade deve ser maior que zero
2. **Saldo resultante nao pode ser negativo** (invariante do agregado)
3. Se saldo insuficiente: rejeitar com code `ESTOQUE_INSUFICIENTE`
4. Saida permitida mesmo em item desativado (para zerar estoque)
5. Toda saida gera Movimentacao com tipo=SAIDA

## Erros de dominio

| Codigo | Quando |
|--------|--------|
| `ESTOQUE_INSUFICIENTE` | Saida com quantidade > saldo atual |
| `QUANTIDADE_INVALIDA` | Quantidade <= 0 |
| `ITEM_NAO_ENCONTRADO` | ID inexistente |

## Invariante — DENTRO do Agregado

```python
# src/estoque/domain/entities/item_estoque.py
class ItemEstoque:
    def registrar_saida(self, quantidade: Quantidade) -> Movimentacao:
        if self.saldo < quantidade.valor:
            raise EstoqueInsuficiente(self.saldo, quantidade.valor)
        self.saldo -= quantidade.valor
        return Movimentacao(tipo=TipoMovimentacao.SAIDA, quantidade=quantidade)
```

O Use Case chama `item.registrar_saida()` — nao faz a validacao de saldo.

## Testes esperados (4)

```
test_registrar_saida
  Entrada de 100 → POST /estoque/{id}/saida quantidade=30 → 201
  GET /estoque/{id} → saldo=70

test_saida_estoque_insuficiente
  Entrada de 10 → POST saida quantidade=20 → 422
  code: ESTOQUE_INSUFICIENTE
  GET /estoque/{id} → saldo=10 (nao alterou)

test_saida_zera_estoque
  Entrada 50 → saida 50 → 201
  GET → saldo=0

test_multiplas_movimentacoes
  Entrada 100 → saida 30 → saida 30 → GET → saldo=40
  GET /movimentacoes → 3 registros (1 entrada + 2 saidas)
```

## Arquivos a modificar (monolito)

```
src/estoque/
├── domain/entities/item_estoque.py   # Adicionar metodo registrar_saida()
├── application/use_cases/
│   └── registrar_saida.py            # NOVO
├── container.py                      # Adicionar provider
└── presentation/
    ├── routes.py                     # Adicionar rota POST /saida
    └── schemas.py                    # Adicionar schema de saida
```

## Criterio de pronto

- [ ] 4 testes passam
- [ ] Invariante `saldo >= 0` validada DENTRO do agregado ItemEstoque
- [ ] Use case NAO faz validacao de saldo (delega ao agregado)
- [ ] `radon cc src/estoque/ -s -a` sem funcao acima de B
- [ ] Endpoints protegidos por JWT
