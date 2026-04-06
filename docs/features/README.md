# Features — Prompts para Implementacao com IA

## Estrategia de Medicao

### Fase A: Construir monolito completo (Features 0-4)

Implementar todas as features no monolito usando Claude Code. Monolito fica 100% funcional.
Nesta fase medimos: tempo, tokens, iteracoes, diff, radon (por feature).

### Fase B: Migrar para microsservicos (3 servicos)

Com o monolito pronto, migrar cada BC para seu microsservico.
Cada migracao tem seu prompt autocontido em `docs/features/migration-X-service.md`.

| # | Prompt | BC | Testes |
|---|--------|----|--------|
| 0 | `migration-0-auth-service.md` | Auth | 6 |
| 1 | `migration-1-catalogo-service.md` | Catalogo | 14 |
| 2 | `migration-2-estoque-service.md` | Estoque + Eventos | 14 |

### Metricas especificas da migracao

| Metrica | O que mostra | Como coletar |
|---------|-------------|-------------|
| Arquivos copiados sem alteracao | domain + application intactos = DDD funcionou | Contar arquivos identicos |
| Arquivos novos | Custo real da migracao | `git diff --stat` |
| % codigo reutilizado | ROI da arquitetura | (copiados / total) * 100 |
| Linhas de domain inalteradas | Isolamento real | `diff` entre monolito e microsservico |
| Linhas de infrastructure novas | Custo de trocar banco | Contar linhas DynamoDB repos |
| Testes que passam | Contrato mantido | pytest |
| Tempo por servico | Esforço com IA | Cronometro |

### Fase C: Adicionar feature nova em ambos (Feature 7)

Feature 7 (Alerta de Estoque Baixo) NAO existe em nenhuma arquitetura.
Implementar em ambos e comparar:
- Tempo para adicionar no monolito (Claude Code)
- Tempo para adicionar nos microsservicos (Claude Code)
- Tempo para adicionar no monolito (Codex)
- Tempo para adicionar nos microsservicos (Codex)

**Esta e a medicao principal do TCC** — mostra o impacto da arquitetura na manutenibilidade.

## Como medir

Para cada implementacao:

1. Abra uma sessao limpa da IA (contexto zerado)
2. Cole o conteudo do arquivo da feature como prompt
3. Inicie cronometro
4. A IA implementa codigo + testes
5. Pare o cronometro quando todos os testes passam
6. Registre na planilha abaixo

## Metricas a coletar

| Metrica | Como |
|---------|------|
| Tempo | Cronometro manual (inicio do prompt → testes passam) |
| Tokens | Exibido pelo Claude Code no final da sessao |
| Iteracoes | Quantas vezes re-promptou ate testes passarem |
| Diff | `git diff --stat` |
| CC antes/depois | `radon cc src/{modulo}/ -s -a` |
| MI antes/depois | `radon mi src/{modulo}/ -s` |
| Cobertura | `pytest --cov=src.{modulo}` |

## Ordem de execucao

### Fase A — Monolito (Claude Code)

| # | Feature | Prompt | Testes |
|---|---------|--------|--------|
| 0 | Auth JWT | `feature-0-auth.md` | 6 |
| 1 | CRUD Categoria | `feature-1-categoria.md` | 5 |
| 2 | CRUD Produto | `feature-2-produto.md` | 9 |
| 3 | Entrada Estoque | `feature-3-entrada.md` | 7 |
| 4 | Saida Estoque | `feature-4-saida.md` | 4 |

### Fase B — Migracao para Microsservicos (Claude Code)

| # | Feature | Prompt | Testes |
|---|---------|--------|--------|
| 0-4 | Migrar Features 0-4 | Migrar camadas presentation + infrastructure | 31 |
| 5 | Eventos de Dominio | `feature-5-eventos.md` | 3 |

### Fase C — Feature Nova (medicao principal)

| # | Arq | IA | Prompt | Testes |
|---|-----|----|--------|--------|
| 7 | Monolito | Claude Code | `feature-7-alerta-estoque.md` | 3 |
| 7 | Monolito | Codex | `feature-7-alerta-estoque.md` | 3 |
| 7 | Microsservicos | Claude Code | `feature-7-alerta-estoque.md` | 3 |
| 7 | Microsservicos | Codex | `feature-7-alerta-estoque.md` | 3 |

### Apos todas as features — Feature 6 (Filtro)

| # | Feature | Prompt | Testes |
|---|---------|--------|--------|
| 6 | Filtro Categoria | `feature-6-filtro.md` | 2 |

## Planilha de coleta

### Fase A — Construcao do Monolito

| Feature | IA | Tempo (min) | Tokens | Iteracoes | Diff | CC antes | CC depois | MI antes | MI depois | Cov % |
|---------|-----|-------------|--------|-----------|------|----------|-----------|----------|-----------|-------|
| 0 Auth | Claude | | | | | | | | | |
| 1 Categoria | Claude | | | | | | | | | |
| 2 Produto | Claude | | | | | | | | | |
| 3 Entrada | Claude | | | | | | | | | |
| 4 Saida | Claude | | | | | | | | | |

### Fase B — Migracao

| Etapa | IA | Tempo (min) | Tokens | Iteracoes | Diff |
|-------|----|-------------|--------|-----------|------|
| Migrar 0-4 | Claude | | | | |
| Feature 5 Eventos | Claude | | | | |

### Fase C — Feature Nova (Alerta Estoque)

| Arq | IA | Tempo (min) | Tokens | Iteracoes | Diff | CC antes | CC depois | MI antes | MI depois |
|-----|----|-------------|--------|-----------|------|----------|-----------|----------|-----------|
| Monolito | Claude | | | | | | | | |
| Monolito | Codex | | | | | | | | |
| Microsservicos | Claude | | | | | | | | |
| Microsservicos | Codex | | | | | | | | |
