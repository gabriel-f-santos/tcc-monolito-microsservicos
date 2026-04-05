# Plano de Execução — TCC

## Visão Geral

Sistema de gerenciamento de produtos e estoque.
Duas versões: monolito (PostgreSQL) e microsserviços serverless (DynamoDB + SNS/SQS).
Objetivo: medir impacto da arquitetura em qualidade, desempenho, custo e produtividade com IA.

---

## Fase 0 — Especificação (antes de qualquer código)

- [x] Linguagem Ubíqua (glossário de termos do domínio)
- [x] Mapa de Bounded Contexts (Catálogo de Produtos × Controle de Estoque)
- [x] Agregados, Entidades e Value Objects de cada contexto
- [x] Contratos de API (endpoints REST com schemas de request/response)
- [x] Eventos de Domínio (ProdutoCriado, ProdutoAtualizado, ProdutoDesativado, EstoqueMovimentado, EstoqueInsuficiente)
- [x] Erros de domínio catalogados
- [x] Regras de negócio consolidadas
- [x] Documento `spec.md` consolidado no repositório

**Produto:** `docs/spec.md`

---

## Fase 1 — Walking Skeleton: Monolito

- [x] Estrutura de pastas DDD: `domain/`, `application/`, `infrastructure/`, `presentation/`
- [x] FastAPI + endpoint `GET /health` (status 200)
- [x] PostgreSQL local (docker-compose)
- [x] Repository Pattern: interface no domínio, implementação SQLAlchemy na infra
- [x] CLAUDE.md com regras de arquitetura e instrução de medição de tempo
- [x] Testes básicos (5 passando, radon baseline CC=A(1.2), MI=100%)

**Produto:** monolito funcional com /health, rodando local

---

## Fase 2 — Walking Skeleton: Microsserviços Serverless

- [x] Dois serviços: `catalogo-service` e `estoque-service`
- [x] Cada um com estrutura DDD própria
- [x] Lambda handlers puros (sem Mangum, sem FastAPI) + `GET /health` em cada um
- [x] `template.yaml` SAM (Lambda + API Gateway + DynamoDB + SNS + SQS)
- [x] Repository Pattern: mesma interface do domínio, implementação DynamoDB (boto3)
- [x] Use Cases idênticos aos do monolito (mesma camada de aplicação)
- [x] CLAUDE.md em cada serviço
- [x] Event consumer Lambda para SQS (skeleton)
- [x] Testes básicos (6 passando, radon baseline CC=A(1.26), MI=100%)

**Produto:** dois serviços no ar com /health, sem lógica de negócio

---

## Fase 3 — CI/CD + Análise Estática

- [x] GitHub Actions: build + deploy automático no push para `main` (path-filtered)
- [x] Pipeline do monolito (test → radon → xenon → Docker → ECR → ASG refresh)
- [x] Pipeline dos microsserviços (test → radon → xenon → sam build → sam deploy)
- [x] Etapa de qualidade: `radon` (CC + MI) + `xenon` (quality gate B/A/A)
- [x] Relatórios salvos como artefatos do CI
- [x] Baseline de métricas (monolito CC=A(1.2) MI=100%, microsserviços CC=A(1.26) MI=100%)

**Produto:** deploy automático funcionando, métricas de qualidade no CI

---

## Fase 4 — Observabilidade

- [x] OpenTelemetry SDK instrumentado no monolito (FastAPI + SQLAlchemy)
- [x] ADOT Lambda Layer configurado no SAM template
- [x] AWS X-Ray ativo no SAM (`Tracing: Active`)
- [x] OTLP exporter configurado para Grafana Cloud (via env vars)
- [ ] Grafana Cloud (free tier) — criar conta e configurar datasources
- [ ] Dashboards: latência por endpoint, error rate, cold start duration
- [ ] Verificar que métricas aparecem antes de adicionar features

**Produto:** Grafana com dashboards funcionais mostrando dados do /health

---

## Fase 5A — Construir Monolito Completo (Claude Code)

Implementar Features 0-4 no monolito. Medir tempo/tokens por feature.
Prompts completos em `docs/features/feature-X-nome.md`.

| # | Feature | Prompt | Testes |
|---|---------|--------|--------|
| 0 | Auth JWT | `feature-0-auth.md` | 6 |
| 1 | CRUD Categoria | `feature-1-categoria.md` | 5 |
| 2 | CRUD Produto | `feature-2-produto.md` | 9 |
| 3 | Entrada Estoque | `feature-3-entrada.md` | 7 |
| 4 | Saida Estoque | `feature-4-saida.md` | 4 |

**Total: 31 testes, monolito 100% funcional ao final**

## Fase 5B — Migrar para Microsservicos (Claude Code)

Com monolito pronto, migrar: trocar presentation (Lambda) + infrastructure (DynamoDB).
Medir tempo total de migracao + Feature 5 (Eventos).

| # | Etapa | Testes |
|---|-------|--------|
| 0-4 | Migrar camadas presentation + infrastructure | 31 |
| 5 | Adicionar Eventos de Domínio (SNS/SQS) | 3 |

## Fase 5C — Feature Nova: Medicao Principal

Feature 7 (Alerta de Estoque Baixo) nao existe em nenhuma arquitetura.
Implementar em ambos, com Claude Code e Codex. **Esta e a medicao principal.**

| Arq | IA | Prompt | Testes |
|-----|----|--------|--------|
| Monolito | Claude Code | `feature-7-alerta-estoque.md` | 3 |
| Monolito | Codex | `feature-7-alerta-estoque.md` | 3 |
| Microsservicos | Claude Code | `feature-7-alerta-estoque.md` | 3 |
| Microsservicos | Codex | `feature-7-alerta-estoque.md` | 3 |

## Fase 5D — Feature Transversal

| # | Feature | Prompt | Testes |
|---|---------|--------|--------|
| 6 | Filtro por Categoria | `feature-6-filtro.md` | 2 |

### Metricas coletadas por feature

| Metrica | Como |
|---------|------|
| Tempo | Cronometro manual (inicio do prompt → testes passam) |
| Tokens | Exibido pelo Claude Code / Codex no final |
| Iteracoes | Quantas vezes re-promptou ate testes passarem |
| Diff | `git diff --stat` |
| CC antes/depois | `radon cc src/{modulo}/ -s -a` |
| MI antes/depois | `radon mi src/{modulo}/ -s` |
| Cobertura | `pytest --cov=src.{modulo}` |

Planilha completa em `docs/features/README.md`.

---

## Fase 6 — Testes de Carga

- [ ] k6 instalado e configurado
- [ ] Cenário 1: carga constante (baseline, 50 req/s por 2 min)
- [ ] Cenário 2: burst (0 → 200 req/s em 10s)
- [ ] Cenário 3: rampa gradual (10 → 100 req/s em 5 min)
- [ ] Capturar: p50, p95, p99, throughput, error rate
- [ ] Rodar nos dois ambientes (monolito e microsserviços)
- [ ] Medir cold starts explicitamente (primeira requisição após período ocioso)
- [ ] Exportar resultados para Grafana

**Produto:** relatório comparativo com gráficos

---

## Fase 7 — Análise de Custos

- [ ] Custo real da AWS após os testes (billing console)
- [ ] Projeção para diferentes cenários de carga (baixa, média, alta)
- [ ] Comparar: monolito (EC2/ECS) vs microsserviços (Lambda + DynamoDB)
- [ ] Discutir: onde serverless faz sentido vs onde não faz

---

## Fase 8 (Opcional) — Chaos Engineering

- [ ] Derrubar produto-service
- [ ] Verificar que estoque-service continua respondendo (dados da projeção local)
- [ ] Capturar métricas no Grafana durante o incidente
- [ ] Se não implementado: discutir teoricamente no artigo

---

## Fase 9 — Escrita do Artigo (30 páginas)

| Seção | Págs | Fonte dos dados |
|-------|------|-----------------|
| Introdução | 2-3 | Contexto e objetivos |
| Fundamentação Teórica | 5-6 | DDD (aggregates, BC vs microsserviço), serverless trade-offs |
| Metodologia | 4 | Ferramentas, como métricas foram coletadas, uso de IA |
| Estudo de Caso: Arquitetura | 5-6 | Spec, código, decisão Postgres→DynamoDB (Repository Pattern) |
| Qualidade e Manutenibilidade | 3-4 | radon, tempo com IA, diff sizes |
| Desempenho e Resiliência | 4-5 | k6, Grafana screenshots, cold starts |
| Custos e Trade-offs | 2 | AWS billing, projeções |
| Conclusão | 1-2 | Limites metodológicos, trabalhos futuros |

---

## Regra de Ouro

> Toda a infraestrutura (Fases 0–4) deve estar 100% funcional ANTES de iniciar a Fase 5.
> Na Fase 5, o único trabalho é: abrir o terminal, pedir a feature para a IA, cronometrar, e fazer deploy.
> Zero configuração de infra durante a medição.
