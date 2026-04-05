# Features — Prompts para Implementacao com IA

## Como usar

Cada arquivo abaixo e um **prompt autocontido**. Para medir tempo de implementacao:

1. Abra uma sessao limpa da IA (Claude Code, Codex, etc)
2. Cole o conteudo do arquivo da feature como prompt
3. Inicie o cronometro
4. A IA implementa codigo + testes
5. Pare o cronometro quando todos os testes passam
6. Registre: tempo, iteracoes, `git diff --stat`, `radon cc/mi` antes e depois

## Ordem de execucao

| # | Feature | Depende de | Monolito | Microsservicos |
|---|---------|-----------|----------|----------------|
| 0 | Auth JWT | — | src/auth/ | auth-service/ |
| 1 | CRUD Categoria | Feature 0 | src/catalogo/ | catalogo-service/ |
| 2 | CRUD Produto | Feature 1 | src/catalogo/ | catalogo-service/ |
| 3 | Entrada Estoque | Feature 2 | src/estoque/ | estoque-service/ |
| 4 | Saida Estoque | Feature 3 | src/estoque/ | estoque-service/ |
| 5 | Eventos de Dominio | Features 1-4 | — | catalogo + estoque |
| 6 | Filtro por Categoria | Features 1-4 | src/estoque/ | estoque-service/ |

## Cada feature e implementada 4 vezes

| Implementacao | Arquitetura | Ferramenta IA |
|--------------|-------------|---------------|
| 1 | Monolito | Claude Code |
| 2 | Monolito | Codex |
| 3 | Microsservicos | Claude Code |
| 4 | Microsservicos | Codex |

## Planilha de coleta

| Feature | Arq | IA | Tempo (min) | Iteracoes | Diff (linhas) | CC antes | CC depois | MI antes | MI depois | Cobertura |
|---------|-----|----|-------------|-----------|---------------|----------|-----------|----------|-----------|-----------|
| | | | | | | | | | | |
