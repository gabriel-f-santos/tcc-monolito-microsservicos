# Registro de Medicoes — TCC

## Fase A — Construcao do Monolito (Claude Code)

### Feature 0: Auth JWT
- **Inicio:** 2026-04-05 21:45
- **Fim:** 2026-04-05 21:51
- **Tempo total:** 6min 02s
- **Modo:** dangerously-skip-permissions
- **Tokens:** (verificar na sessao)
- **Iteracoes:** 1 (prompt unico, sem re-prompt)
- **Diff:** 12 arquivos novos, 6 modificados, ~408 linhas novas + 49 linhas em arquivos existentes
- **CC antes:** A (1.2)
- **CC depois:** A (1.69) — middleware B(6), demais A
- **MI antes:** 100%
- **MI depois:** A (media ~87%) — login.py 55.73, middleware 58.98, repo 59.33
- **Cobertura:** (rodar pytest --cov)
- **Testes:** 6/6 passando (11 total com os anteriores)
- **Observacoes:** Feature completa em 1 prompt. Usou dependency-injector corretamente. Criou container, middleware JWT, use cases, repository SQLAlchemy, domain entities/exceptions. Seguiu estrutura DDD por dominio conforme docs.

### Feature 1: CRUD Categoria
- **Inicio:** 2026-04-05 22:42
- **Fim:** 2026-04-05 22:45
- **Tempo total:** 2min 25s
- **Modo:** dangerously-skip-permissions
- **Tokens:** (verificar na sessao)
- **Iteracoes:** 1
- **Diff:** 14 arquivos, +412 linhas
- **CC antes:** A (1.69)
- **CC depois:** A (1.74) — tudo A, nenhuma acima de B
- **MI antes:** A (87%)
- **MI depois:** A (~90%) — catalogo repo 53.63, entidade 63.82
- **Cobertura:** (rodar pytest --cov)
- **Testes:** 5/5 (16 total)
- **Observacoes:** Completou em 1 prompt. Seguiu RULES.md: __post_init__ na entidade, sem libs externas no app layer. Container com wiring_config.

### Feature 2: CRUD Produto
- **Inicio:** 2026-04-05 23:01
- **Fim:** 2026-04-05 23:04
- **Tempo total:** 3min 44s
- **Modo:** dangerously-skip-permissions
- **Tokens:** (verificar na sessao)
- **Iteracoes:** 1
- **Diff:** 7 arquivos, +224 linhas (novos: produto.py, sku.py, dinheiro.py, 5 use cases, repo)
- **CC antes:** A (1.74)
- **CC depois:** A (2.03) — 86 blocos analisados
- **MI antes:** A (~90%)
- **MI depois:** 
- **Cobertura:** 
- **Testes:** 9/9 (25 total)
- **Observacoes:** Completou em 1 prompt. Criou VOs (SKU, Dinheiro), agregado Produto, 5 use cases, repo SQLAlchemy. Reusou container e routes existentes do catalogo.

### Feature 3: Entrada Estoque
- **Inicio:** 2026-04-05 23:18
- **Fim:** 2026-04-05 23:28
- **Tempo total:** 9min 54s
- **Modo:** dangerously-skip-permissions
- **Tokens:** (verificar na sessao)
- **Iteracoes:** 
- **Diff:** 23 arquivos, +115 linhas (mod) + novos (container, 4 use cases, 2 entities, 2 VOs, 2 repos, routes, schemas)
- **CC antes:** A (2.03)
- **CC depois:** A (1.85) — estoque 62 blocos
- **MI antes:** 
- **MI depois:** 
- **Cobertura:** 
- **Testes:** 7/7 (32 total)
- **Observacoes:** Feature mais demorada (9min54s vs 3min44s anterior). Segundo BC completo, novo container, movimentacao, VOs (Quantidade, TipoMovimentacao). Atualizou EstoqueService para incluir projecao (sku, nome, categoria).

### Feature 4: Saida Estoque
- **Inicio:** 2026-04-05 23:45
- **Fim:** 2026-04-05 23:48
- **Tempo total:** 2min 45s
- **Modo:** dangerously-skip-permissions
- **Tokens:** 
- **Iteracoes:** 
- **Diff:** 
- **CC antes:** A (1.85)
- **CC depois:** 
- **MI antes:** 
- **MI depois:** 
- **Cobertura:** 
- **Testes:** 4/4 (36 total)
- **Observacoes:** Feature mais rapida. Adicionou registrar_saida() no agregado ItemEstoque, rota e testes. Diff limpo — 6 arquivos, +197 linhas.

---

## Fase B — Migracao para 6 Microsservicos (Claude Code, agentes paralelos)

6 agentes Claude Code em paralelo migraram os monolitos para microsservicos
serverless (Lambda + DynamoDB + SNS/SQS). Cada servico tem sua propria stack
CloudFormation, API Gateway e tabelas DynamoDB.

### Resultados por servico

| Servico | Arq | Testes | Tempo | Deploy | E2E |
|---------|-----|--------|-------|--------|-----|
| auth-service | DDD | 12/12 | 4min 33s | OK | OK |
| catalogo-service | DDD | 20/20 | 3min 41s | OK | OK |
| estoque-service | DDD | 20/20 | 4min 23s | OK | OK |
| auth-service-mvc | MVC | 12/12 | 1min 52s | — | — |
| catalogo-service-mvc | MVC | 20/20 | 2min 23s | — | — |
| estoque-service-mvc | MVC | 20/20 | 2min 31s | — | — |

### Totais DDD vs MVC

| Metrica | DDD | MVC | Delta |
|---------|-----|-----|-------|
| Tempo somado | 12min 36s | 6min 46s | MVC 46% mais rapido |
| Tempo paralelo (max) | 4min 33s | 2min 31s | MVC 44% mais rapido |
| Testes passando | 52/52 | 52/52 | — |
| Iteracoes | 1 cada | 1 cada | — |
| Deploy + E2E validado | 3/3 | (nao deployado) | — |

### Metricas de qualidade (radon/grimp/cohesion)

| Codebase | SLOC | CC medio | MI medio | Pacotes | Instab. media |
|----------|------|----------|----------|---------|---------------|
| Monolito DDD | 1821 | 1.84 | 90.28 | 6 | 0.417 |
| Monolito MVC | 466 | 1.86 | 75.04 | 4 | 0.000 |
| Auth DDD | 344 | 1.73 | 93.25 | 6 | 0.458 |
| Catalogo DDD | 676 | 2.31 | 81.89 | 5 | 0.450 |
| Estoque DDD | 685 | 2.22 | 87.28 | 5 | 0.450 |
| Auth MVC | 103 | 2.50 | 88.66 | 1 | 0.000 |
| Catalogo MVC | 240 | 3.90 | 83.13 | 1 | 0.000 |
| Estoque MVC | 257 | 2.82 | 80.54 | 1 | 0.000 |

### Validacao E2E em producao (DDD)

```
registrar → 201  |  login → 200 + JWT  |  criar categoria → 201
criar produto → 201 + SNS  |  (8s) SNS→SQS→estoque → item saldo=0
entrada 100 → 201  |  saida 30 → 201  |  buscar → saldo=70  |  movimentacoes → 2
```

---

## Fase C — Feature Nova: Alerta Estoque Baixo (Medicao Principal)

### Monolito + Claude Code
- **Inicio:** 
- **Fim:** 
- **Tempo total:** 
- **Tokens:** 
- **Iteracoes:** 
- **Diff:** 
- **CC antes:** 
- **CC depois:** 
- **MI antes:** 
- **MI depois:** 
- **Testes:** /3
- **Observacoes:** 

### Monolito + Codex
- **Inicio:** 
- **Fim:** 
- **Tempo total:** 
- **Tokens:** 
- **Iteracoes:** 
- **Diff:** 
- **CC antes:** 
- **CC depois:** 
- **MI antes:** 
- **MI depois:** 
- **Testes:** /3
- **Observacoes:** 

### Microsservicos + Claude Code
- **Inicio:** 
- **Fim:** 
- **Tempo total:** 
- **Tokens:** 
- **Iteracoes:** 
- **Diff:** 
- **CC antes:** 
- **CC depois:** 
- **MI antes:** 
- **MI depois:** 
- **Testes:** /3
- **Observacoes:** 

### Microsservicos + Codex
- **Inicio:** 
- **Fim:** 
- **Tempo total:** 
- **Tokens:** 
- **Iteracoes:** 
- **Diff:** 
- **CC antes:** 
- **CC depois:** 
- **MI antes:** 
- **MI depois:** 
- **Testes:** /3
- **Observacoes:** 

---

## Fase D — Feature Transversal

### Feature 6: Filtro por Categoria
- **Inicio:** 
- **Fim:** 
- **Tempo total:** 
- **Tokens:** 
- **Iteracoes:** 
- **Diff:** 
- **Testes:** /2
- **Observacoes:** 
