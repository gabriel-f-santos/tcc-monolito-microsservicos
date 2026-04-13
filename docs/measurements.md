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

## Fase C — Feature Nova: Alerta Estoque Baixo

4 agentes em paralelo implementaram a mesma feature em 4 variantes.
Testes pre-escritos (4 por variante). Spec: `docs/features/spec-alerta-estoque-baixo.md`.

### Resultados por variante

| Variante | Tempo | Testes (novos/total) | CC antes | CC depois | MI antes | MI depois | Iteracoes |
|----------|-------|---------------------|----------|-----------|----------|-----------|-----------|
| Monolito DDD | 3min 31s | 4/40 | 1.84 | 1.86 | 90.28 | 89.39 | 1 |
| Monolito MVC | 1min 53s | 4/37 | 1.86 | 1.88 | 75.04 | 75.08 | 1 |
| Microsservico DDD | 3min 01s | 4/24 | 2.22 | 2.17 | 87.28 | 85.51 | 1 |
| Microsservico MVC | 1min 35s | 4/24 | 2.82 | 3.12 | 80.54 | 79.53 | 1 |

### Comparacao DDD vs MVC

| Metrica | DDD (monolito) | MVC (monolito) | DDD (micro) | MVC (micro) |
|---------|---------------|---------------|-------------|-------------|
| Tempo | 3min 31s | **1min 53s** | 3min 01s | **1min 35s** |
| Delta CC | +0.02 | +0.02 | **-0.05** | +0.30 |
| Delta MI | -0.89 | +0.04 | -1.77 | -1.01 |
| Arqs novos | 5 | 0 | 4 | 0 |
| Arqs modificados | 7 | 3 | 5 | 2 |

### Observacoes

- MVC ~47% mais rapido que DDD (mesmo padrao da migracao)
- DDD toca mais arquivos (novas entidades, repos, use cases, rotas) vs MVC (tudo inline em 2-3 arquivos)
- CC praticamente estavel em todas as variantes (+/- 0.3 pontos) — feature pequena nao altera complexidade significativamente
- MI com leve queda no DDD microsservico (-1.77) pela adicao de novos arquivos de infra (repo DynamoDB)
- DDD microsservico precisou adicionar tabela `AlertasTable` no template.yaml + env var `ALERTAS_TABLE` — conftest.py auto-criou no moto sem intervencao
- Todos os 4 convergiram na primeira tentativa, zero testes quebrados

---

## Teste de Carga — Latencia (k6)

Teste com k6 v0.55.0. Ramp-up 1→5 VUs (15s), sustain 10 VUs (60s), ramp-down (10s).
Fluxo: registrar → login → categoria → produto → estoque → entrada → saida.

### Latencia por endpoint: Monolito DDD (EC2/ALB) vs Microsservicos DDD (Lambda)

| Endpoint | Alvo | p50 | p90 | p95 | avg |
|----------|------|-----|-----|-----|-----|
| health | Monolito | 137ms | 250ms | 253ms | 174ms |
| health | Micro | 373ms | 486ms | 501ms | 316ms |
| registrar | Monolito | 887ms | 1323ms | 1445ms | 913ms |
| registrar | Micro | 1530ms | 1648ms | 1734ms | 1532ms |
| login | Monolito | 917ms | 1311ms | 1416ms | 896ms |
| login | Micro | 1460ms | 1517ms | 1613ms | 1479ms |
| criar_categoria | Monolito | 147ms | 250ms | 253ms | 177ms |
| criar_categoria | Micro | 497ms | 562ms | 651ms | 530ms |
| criar_produto | Monolito | 194ms | 252ms | 255ms | 207ms |
| criar_produto | Micro | 635ms | 739ms | 752ms | 588ms |
| buscar_estoque | Micro | 264ms | 505ms | 530ms | 369ms |
| entrada | Micro | 426ms | 694ms | 723ms | 489ms |
| saida | Micro | 445ms | 684ms | 746ms | 506ms |

### Analise

- **Monolito 2-3x mais rapido em p50** nos endpoints comparaveis (health, registrar, login, categoria, produto)
- **Registrar/login** sao os mais lentos em ambos (~900ms monolito, ~1500ms micro) por causa do bcrypt hash
- **CRUD simples** (categoria, produto): monolito ~150-200ms vs micro ~500-650ms — overhead do API Gateway + Lambda cold start
- **Estoque** (entrada, saida): micro ~450-500ms p50 — operacoes DynamoDB com Scan
- Microsservicos tem **p90/p95 mais previsivel** (menos dispersao) — Lambda escala horizontal automaticamente
- Monolito tem **p95 mais alto relativo ao p50** (250ms→1445ms no registrar) — t3.micro saturando com bcrypt sincrono

### Configuracao

- Monolito: EC2 t3.micro, 1 instancia, ALB, RDS PostgreSQL
- Microsservicos: Lambda 512MB, API Gateway, DynamoDB PAY_PER_REQUEST
- Teste rodado de maquina local (latencia de rede incluida em ambos)
- Ferramenta: k6 v0.55.0, 10 VUs max
