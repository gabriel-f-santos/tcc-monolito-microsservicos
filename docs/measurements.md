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
- **Cobertura:** 
- **Testes:** /4
- **Observacoes:** 

---

## Fase B — Migracao para Microsservicos (Claude Code)

### Migracao Features 0-4
- **Inicio:** 
- **Fim:** 
- **Tempo total:** 
- **Tokens:** 
- **Iteracoes:** 
- **Diff:** 
- **Testes:** /31
- **Observacoes:** 

### Feature 5: Eventos de Dominio
- **Inicio:** 
- **Fim:** 
- **Tempo total:** 
- **Tokens:** 
- **Iteracoes:** 
- **Diff:** 
- **Testes:** /3
- **Observacoes:** 

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
