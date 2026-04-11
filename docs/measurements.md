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

## Fase B — Migracao para Microsservicos (Claude Code)

### Migration 0: Auth Service
- **Inicio:** 2026-04-07 20:53
- **Fim:** 2026-04-07 20:58
- **Tempo total:** 4min 47s
- **Modo:** dangerously-skip-permissions
- **Tokens:** 
- **Iteracoes:** 1
- **Arquivos copiados (domain+app):** 7/7 (4 identicos, 3 so import paths)
- **Arquivos novos (infra+presentation+container):** 8
- **% codigo reutilizado:** 46% arquivos, ~95% linhas (diffs sao so import paths)
- **Testes:** 6/6 auth + 2 health = 8 passando
- **Observacoes:** Lógica 100% identica ao monolito. Domain e Application copiados. Infra services (bcrypt, jose) copiados. Novos: DynamoDB repo, Lambda handlers, authorizer, container.

### Migration 1: Catalogo Service
- **Inicio:** 2026-04-07 21:00
- **Fim:** 2026-04-07 21:07
- **Tempo total:** 6min 57s
- **Modo:** dangerously-skip-permissions
- **Tokens:** 
- **Iteracoes:** 1
- **Arquivos copiados (domain+app):** 15 (4 identicos, 11 import-path-only)
- **Arquivos novos (infra+presentation+container):** 6 (2 DynamoDB repos, SNS service, handler, settings, container)
- **% codigo reutilizado:** 71% arquivos, ~95% linhas
- **Testes:** 14/14 catalogo + 2 health = 16 passando
- **Observacoes:** Maior BC — 8 use cases, 2 VOs, 2 repos. SNS EstoqueService substitui in-process. Handler com roteamento por method+path.

### Migration 2: Estoque Service (inclui eventos)
- **Inicio:** 2026-04-07 ~21:10
- **Fim:** 2026-04-07 ~21:17
- **Tempo total:** 6min 24s (segunda tentativa — primeira falhou e entrou em modo planejamento)
- **Modo:** dangerously-skip-permissions
- **Tokens:** 
- **Iteracoes:** 2 (primeira falhou)
- **Arquivos copiados (domain+app):** 14
- **Arquivos novos (infra+presentation+eventos+container):** 6
- **% codigo reutilizado:** 70% arquivos, ~95% linhas
- **Testes:** 14/14 estoque + 3 eventos + 1 consumer = 18 passando
- **Observacoes:** Primeira tentativa entrou em modo planejamento — git clean e reiniciou. Inclui event consumer para SQS (ProdutoCriado, ProdutoAtualizado, ProdutoDesativado).
- **Observacoes:** 

---

## Fase B2 — Migracao MVC para Microsservicos (Agentes Paralelos)

### Migration MVC 0: Auth Service
- **Tempo total:** 2min 26s
- **Modo:** agente paralelo (subagent)
- **Testes:** 6/6 auth + 2 health = 8 passando
- **% codigo reutilizado do monolito-mvc:** 0% (reescrita completa)
- **Observacoes:** SQLAlchemy → DynamoDB boto3 inline. Nenhuma linha copiada do monolito-mvc.

### Migration MVC 1: Catalogo Service
- **Tempo total:** 2min 11s
- **Modo:** agente paralelo (subagent)
- **Testes:** 14/14 catalogo + 2 health = 16 passando
- **% codigo reutilizado do monolito-mvc:** 0% (reescrita completa)
- **Observacoes:** Handler com roteamento por method+path. SNS publish inline.

### Migration MVC 2: Estoque Service
- **Tempo total:** 3min 41s
- **Modo:** agente paralelo (subagent)
- **Testes:** 11/11 estoque + 3 eventos + 2 health = 16 passando
- **% codigo reutilizado do monolito-mvc:** 0% (reescrita completa)
- **Observacoes:** Event consumer para SQS. Mais demorado por ter mais logica.

### Totais MVC Migration

| Metrica | DDD Migration | MVC Migration |
|---------|--------------|---------------|
| Tempo total | 18min 08s | 8min 18s |
| Testes | 34/34 | 40/40 |
| % reuso (linhas) | ~95% | ~0% |
| Arquivos copiados | 34 | 0 |
| Arquivos novos | 24 | 8 |

---

## Fase B4 — Rodada 2: Migracao com INTEGRATION-CONTRACT + moto + testes-guardiao

Reexecucao da migracao apos auditoria da rodada 1 que encontrou **4 de 6
microsservicos quebrados no deploy real** (bugs de integracao AWS que os
testes InMemory mascaravam). Antes desta rodada, o skeleton recebeu:

- `INTEGRATION-CONTRACT.md` com 6 regras obrigatorias
- `conftest.py` generico parseando `template.yaml` e subindo moto
- `tests/test_integration_contract.py` com 4 testes-guardiao
- Prompts atualizados com contexto dos 4 bugs anteriores + checklist de done

### Branch: `migration/v2-run1` (a partir de `skeleton-microsservicos-v2`)

### Resultados (medicoes via `scripts/migration-timer.sh`)

| Servico | Arq | Testes | Tempo (s) | Tempo (min) | Bugs? | Iteracoes |
|---------|-----|--------|-----------|-------------|-------|-----------|
| auth-service | DDD | 12/12 | 272.284 | 4.54 | 0 | 1 |
| catalogo-service | DDD | 20/20 | 220.689 | 3.68 | 0 | 1 |
| estoque-service | DDD | 20/20 | 262.943 | 4.38 | 0 | 1 |
| auth-service-mvc | MVC | 12/12 | 111.635 | 1.86 | 0 | 1 |
| catalogo-service-mvc | MVC | 20/20 | 143.149 | 2.39 | 0 | 1 |
| estoque-service-mvc | MVC | 20/20 | 151.346 | 2.52 | 0 | 1 |

### Totais

| Metrica | DDD | MVC | Delta |
|---------|-----|-----|-------|
| Tempo somado | 755.9s (12.6min) | 406.1s (6.77min) | MVC 46% mais rapido |
| Tempo paralelo (max) | 272.3s (4.54min) | 151.3s (2.52min) | MVC 44% mais rapido |
| Testes passando | 52/52 | 52/52 | — |
| 1a tentativa bem-sucedida | 3/3 | 3/3 | **100%** |

### Comparacao Rodada 1 (main, sem contrato) vs Rodada 2 (com contrato)

| Metrica | Rodada 1 | Rodada 2 | Delta |
|---------|----------|----------|-------|
| Tempo DDD (paralelo max) | 3min 54s | 4min 33s | +17% (+39s) |
| Tempo MVC (paralelo max) | 2min 13s | 2min 31s | +14% (+18s) |
| Testes locais verdes | 80/80 | 104/104 | +24 (guardioes) |
| **Servicos funcionais em deploy real** | **2/6** | **(a validar)** | — |
| Bugs graves detectados | 4 (so apos deploy) | 0 (antes do deploy) | — |

**Observacoes:**
- O contrato custou ~15% mais tempo de implementacao (esperado — mais testes, mais constraints)
- Em troca, **zero bugs de integracao na primeira tentativa** — todos os 6 agentes entregaram codigo alinhado com o deploy real, pelos testes-guardiao
- 24 novos testes aparecem no total: 4 testes-guardiao × 6 servicos
- Ambos os agentes de estoque (DDD e MVC) reportaram bug de docstring em `tests/test_estoque.py` — fix aplicado por ambos. O bug estava no skeleton
- Todos os 6 convergiram para padroes similares: `_table()` funcao lazy, env vars dentro de funcoes, zero chamada boto3 em import-time

### Validacao

```bash
$ for svc in auth-service catalogo-service estoque-service \
             auth-service-mvc catalogo-service-mvc estoque-service-mvc; do
    cd microsservicos/$svc && .venv/bin/pytest tests/ -q
  done
12 passed / 20 passed / 20 passed / 12 passed / 20 passed / 20 passed
→ 104/104 total
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
