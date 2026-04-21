# Revisao Completa do TCC — Relatorio de Auditoria

**Data:** 2026-04-10
**Revisor:** Assistente de revisao automatizado
**Documento revisado:** `/home/gabriel/Documents/tcc/project/docs/tcc.md`
**Fontes de verificacao:** `measurements.md`, `metrics-report.md`, `SKILL.md`

---

## 1. Checklist de formatacao

### 1.1 Citacoes

- [x] Todas indiretas (nenhuma citacao direta encontrada)
- [x] Formato Sobrenome (ano) correto na maioria dos casos
- [x] Maiuscula so na 1a letra dos sobrenomes
- [x] Nenhum uso de *apud*
- [ ] **PROBLEMA:** "et al." aparece sem italico em todas as ocorrencias (linhas 148, 215, 286). Latim deve ser em *italico* (*et al.*)

### 1.2 Siglas

- [x] DDD expandido na Introducao: "Domain-Driven Design [DDD]" (linha 146)
- [x] MVC expandido na Introducao: "Model-View-Controller [MVC]" (linha 152)
- [x] CC expandido na Introducao: "Complexidade Ciclomatica [CC]" (linha 148)
- [x] IM expandido na Introducao: "Indice de Manutenibilidade [IM]" (linha 148)
- [x] BC, SNS, SQS, API, ASGI, JWT, CRUD, SAM, ALB, LCOM, VU, IA — todos expandidos na primeira ocorrencia no corpo
- [x] Resumo usa siglas sem expansao (permitido pela regra)
- [ ] **PROBLEMA:** "CPU" (linha 341) aparece entre aspas como termo estrangeiro mas nunca e expandido como sigla: "Central Processing Unit" [CPU]
- [ ] **PROBLEMA:** SLOC e expandido como "linhas de codigo executavel [SLOC]" (linha 230), mas a expansao correta seria "Source Lines of Code" [SLOC] — o acronimo em ingles nao corresponde a traducao fornecida. Sugestao: usar a forma inglesa entre aspas ou explicar que SLOC corresponde a "Source Lines of Code"

### 1.3 Expressoes estrangeiras

- [x] "serverless", "Bounded Contexts", "Clean Architecture", "Repository Pattern", "framework", "handler", "cold start", "overhead", "endpoint", "Value Objects", "feature", "login", "token", "prompt", "Walking Skeleton", "fitness function", etc. — todas entre aspas
- [ ] **PROBLEMA CRITICO:** *et al.* (latim) deve estar em italico, nao em texto normal. Ocorrencias: Ford et al. (2022) na linha 148; Coleman et al. (1994) nas linhas 215, 286

### 1.4 Introducao

- [x] Sem subtopicos
- [x] Sem figuras ou tabelas
- [x] Extensao estimada: ~650 palavras (~1,5-2 paginas em Arial 11, espac. 1,5). Dentro do limite de 2 paginas
- [x] Contem contexto, problema, lacuna, objetivo — estrutura adequada
- [ ] **PROBLEMA:** Falta paragrafo de estrutura do artigo (§5 sugerido no TODO). Nao e obrigatorio, mas recomendado

### 1.5 Material e Metodos

- [x] Subtopicos em negrito com recuo (formato Markdown: **Negrito**)
- [ ] **PROBLEMA CRITICO:** Uso de presente do indicativo em vez de preterito perfeito impessoal em diversas passagens:
  - Linha 164: "O contexto de Catalogo **possui** como raiz de agregacao..." → deveria ser "possuia" ou reestruturar ("O contexto de Catalogo **foi modelado com** a raiz de agregacao...")
  - Linha 164: "**mantem** um saldo calculado" → "mantinha" ou "foi modelado para manter"
  - Linha 164: "O Estoque **nao conhece** o dominio" → "O Estoque nao conhecia" ou "foi projetado para nao conhecer"
  - Linha 164: "**mantem** apenas uma projecao local" → "mantinha"
  - Linha 170: "o codigo **foi** estruturado" (OK — preterito)
  - Linha 178: "cada Bounded Context **possuia** um container" (OK)
  - Linha 178: "Os casos de uso **recebiam** interfaces" (OK)
  - Linha 178: "**desconheciam** se estavam conectados" (OK — mas mistura com presente em outros trechos)

  **Resumo:** A secao alterna entre preterito (correto) e presente (incorreto). A regra exige preterito perfeito impessoal em toda a secao.

### 1.6 Resultados e Discussao

- [x] Subtopicos em negrito
- [x] Tabelas com titulo acima (em comentarios HTML) e fonte abaixo (em comentarios HTML)
- [x] Tabelas numeradas sequencialmente (2 a 6)
- [ ] **PROBLEMA:** Nao existe Tabela 1 no corpo do texto. Ha um TODO para "Tabela 1. Metricas coletadas, ferramentas e dimensoes de avaliacao" na secao Material e Metodos (linha 221), mas ela nunca foi inserida. A numeracao das tabelas no texto pula de 1 para 2. Se a Tabela 1 nao for inserida, as demais devem ser renumeradas (2→1, 3→2, ..., 6→5)
- [ ] **PROBLEMA MENOR:** Os titulos e fontes das tabelas estao apenas em comentarios HTML. Ao converter para Word, e necessario garantir que sejam inseridos como texto visivel com formatacao correta

### 1.7 Conclusao

- [x] Sem tabelas ou figuras
- [x] Responde ao objetivo da Introducao
- [x] Menciona limitacoes
- [x] Sugere trabalhos futuros
- [ ] **PROBLEMA MENOR:** Alguns paragrafos sao longos (especialmente o paragrafo sobre produtividade com IA, ~120 palavras). A regra recomenda "frases curtas com conclusoes e inferencias"

### 1.8 Referencias

- [x] Ordem alfabetica correta (Chidamber, Coleman, Evans, Ford, Halstead, Martin 1994, Martin 2017, McCabe, Newman 2019, Newman 2021, Percival, Richards, Vernon)
- [x] Todas as citacoes do texto tem entrada correspondente nas Referencias
- [x] Todas as entradas nas Referencias sao citadas no texto
- [x] Formato de periodico correto (Chidamber e Kemerer, Coleman et al., McCabe)
- [x] Formato de livro correto (Evans, Ford et al., Halstead, Martin 2017, Newman 2019/2021, Percival e Gregory, Richards e Ford, Vernon)
- [ ] **PROBLEMA MENOR:** Martin (1994) esta listado como "Object Mentor, Gurnee, IL, USA" — e um documento tecnico/white paper, nao um livro nem periodico. O formato nao se encaixa perfeitamente nas categorias do manual USP/ESALQ. Sugestao: verificar se ha publicacao em periodico que possa substituir, ou formatar como documento tecnico

### 1.9 Correspondencia citacoes ↔ referencias

| Citacao no texto | Entrada nas Referencias | Status |
|-----------------|------------------------|--------|
| Newman (2021) | Newman, S. 2021. Building Microservices... | OK |
| Richards e Ford (2020) | Richards, M.; Ford, N. 2020. Fundamentals... | OK |
| Evans (2003) | Evans, E. 2003. Domain-Driven Design... | OK |
| Vernon (2013) | Vernon, V. 2013. Implementing DDD... | OK |
| Martin (2017) | Martin, R.C. 2017. Clean Architecture... | OK |
| Percival e Gregory (2020) | Percival, H.; Gregory, B. 2020. Architecture Patterns... | OK |
| Newman (2019) | Newman, S. 2019. Monolith to Microservices... | OK |
| Ford et al. (2022) | Ford, N.; Richards, M.; Sadalage, P.; Dehghani, Z. 2022... | OK |
| McCabe (1976) | McCabe, T.J. 1976. A complexity measure... | OK |
| Coleman et al. (1994) | Coleman, D.; Ash, D.; Lowther, B.; Oman, P. 1994... | OK |
| Halstead (1977) | Halstead, M.H. 1977. Elements of Software Science... | OK |
| Martin (1994) | Martin, R.C. 1994. OO Design Quality Metrics... | OK |
| Chidamber e Kemerer (1994) | Chidamber, S.R.; Kemerer, C.F. 1994... | OK |

**Resultado:** 13 citacoes, 13 referencias. Correspondencia completa.

---

## 2. Verificacao de dados

### 2.1 Tabela 2 — CC e IM por base de codigo

| Metrica no artigo | Valor no artigo | Valor em metrics-report.md | Status |
|-------------------|----------------|---------------------------|--------|
| Monolito DDD SLOC | 1821 | 1821 | OK |
| Monolito DDD CC | 1,84 | 1.84 | OK |
| Monolito DDD IM | 90,28 | 90.28 | OK |
| Monolito MVC SLOC | 466 | 466 | OK |
| Monolito MVC CC | 1,86 | 1.86 | OK |
| Monolito MVC IM | 75,04 | 75.04 | OK |
| Auth DDD SLOC | 344 | 344 | OK |
| Auth DDD CC | 1,73 | 1.73 | OK |
| Auth DDD IM | 93,25 | 93.25 | OK |
| Catalogo DDD SLOC | 676 | 676 | OK |
| Catalogo DDD CC | 2,31 | 2.31 | OK |
| Catalogo DDD IM | 81,89 | 81.89 | OK |
| Estoque DDD SLOC | 685 | 685 | OK |
| Estoque DDD CC | 2,22 | 2.22 | OK |
| Estoque DDD IM | 87,28 | 87.28 | OK |
| Auth MVC SLOC | 103 | 103 | OK |
| Auth MVC CC | 2,50 | 2.50 | OK |
| Auth MVC IM | 88,66 | 88.66 | OK |
| Catalogo MVC SLOC | 240 | 240 | OK |
| Catalogo MVC CC | 3,90 | 3.90 | OK |
| Catalogo MVC IM | 83,13 | 83.13 | OK |
| Estoque MVC SLOC | 257 | 257 | OK |
| Estoque MVC CC | 2,82 | 2.82 | OK |
| Estoque MVC IM | 80,54 | 80.54 | OK |

### 2.2 Medias globais calculadas (verificacao)

| Metrica | Calculo | Resultado | Valor no artigo | Status |
|---------|---------|-----------|----------------|--------|
| CC medio DDD (4 bases) | (1.84+1.73+2.31+2.22)/4 | 2.025 | 2,03 | OK (arredondamento) |
| CC medio MVC (4 bases) | (1.86+2.50+3.90+2.82)/4 | 2.77 | 2,77 | OK |
| Diferenca CC % | (2.77-2.025)/2.77 | 26.9% | 27% | OK (arredondamento) |
| IM medio DDD (4 bases) | (90.28+93.25+81.89+87.28)/4 | 88.175 | 88,18 | OK |
| IM medio MVC (4 bases) | (75.04+88.66+83.13+80.54)/4 | 81.8425 | 81,84 | OK |
| Diferenca IM | 88.175 - 81.8425 | 6.33 | 6,3 | OK (arredondamento) |
| IM monolito delta | 90.28 - 75.04 | 15.24 | 15,2 | OK (arredondamento) |

### 2.3 Tabela 3 — Acoplamento e coesao

| Metrica no artigo | Valor no artigo | Valor em metrics-report.md | Status |
|-------------------|----------------|---------------------------|--------|
| Monolito DDD — Pacotes | 6 | 6 | OK |
| Monolito DDD — Modulos | 117 | 117 | OK |
| Monolito DDD — Instab. | 0,417 | 0.417 | OK |
| Monolito DDD — Classes | 87 | 87 | OK |
| Monolito DDD — Coesao | 32,29 | 32.29 | OK |
| (Todas as demais linhas) | — | — | OK (verificadas uma a uma) |

### 2.4 Tabela 4 — Latencia

| Endpoint/Alvo | Metrica | Artigo | measurements.md | Status |
|---------------|---------|--------|----------------|--------|
| health / Monolito | p50 | 137 | 137ms | OK |
| health / Micro | p50 | 373 | 373ms | OK |
| registrar / Monolito | p50 | 887 | 887ms | OK |
| registrar / Micro | p50 | 1530 | 1530ms | OK |
| login / Monolito | p50 | 917 | 917ms | OK |
| login / Micro | p50 | 1460 | 1460ms | OK |
| criar categoria / Monolito | p50 | 147 | 147ms | OK |
| criar categoria / Micro | p50 | 497 | 497ms | OK |
| criar produto / Monolito | p50 | 194 | 194ms | OK |
| criar produto / Micro | p50 | 635 | 635ms | OK |
| buscar estoque / Micro | p50 | 264 | 264ms | OK |
| entrada estoque / Micro | p50 | 426 | 426ms | OK |
| saida estoque / Micro | p50 | 445 | 445ms | OK |
| (p90 e p95 de todos) | — | — | — | OK (todos conferidos) |

### 2.5 Tabela 5 — Tempos de implementacao

| Fase | Variante | Artigo | measurements.md | Status |
|------|----------|--------|----------------|--------|
| Construcao monolito DDD | Tempo | 24min 50s | 6:02+2:25+3:44+9:54+2:45 = 24min50s | OK |
| Construcao monolito DDD | Testes | 36 | 36 total | OK |
| Construcao monolito DDD | SLOC | 1821 | 1821 | OK |
| Construcao monolito MVC | Tempo | ~8min | ~8min | OK |
| Construcao monolito MVC | Testes | 33 | 33 | OK |
| Construcao monolito MVC | SLOC | 466 | 466 | OK |
| Migracao DDD (somado) | Tempo | 12min 36s | 4:33+3:41+4:23 = 12min37s | **MENOR: 1s de diferenca** |
| Migracao MVC (somado) | Tempo | 6min 46s | 1:52+2:23+2:31 = 6min46s | OK |
| Migracao DDD (paralelo) | Tempo | 4min 33s | max(4:33, 3:41, 4:23) = 4:33 | OK |
| Migracao MVC (paralelo) | Tempo | 2min 31s | max(1:52, 2:23, 2:31) = 2:31 | OK |
| Migracao DDD | Testes | 52/52 | 12+20+20=52 | OK |
| Migracao MVC | Testes | 52/52 | 12+20+20=52 | OK |
| Feature mono DDD | Tempo | 3min 31s | 3min 31s | OK |
| Feature mono MVC | Tempo | 1min 53s | 1min 53s | OK |
| Feature micro DDD | Tempo | 3min 01s | 3min 01s | OK |
| Feature micro MVC | Tempo | 1min 35s | 1min 35s | OK |

### 2.6 Tabela 6 — Comparacao cruzada

| Metrica | Artigo | Calculo/Fonte | Status |
|---------|--------|--------------|--------|
| SLOC monolito DDD | 1821 | metrics-report: 1821 | OK |
| SLOC monolito MVC | 466 | metrics-report: 466 | OK |
| DDD ~3,9x maior | 3,9x | 1821/466 = 3.91 | OK |
| CC global DDD | 2,03 | Calculado: 2.025 | OK |
| CC global MVC | 2,77 | Calculado: 2.77 | OK |
| DDD 27% menor | 27% | Calculado: 26.9% | OK |
| IM global DDD | 88,18 | Calculado: 88.175 | OK |
| IM global MVC | 81,84 | Calculado: 81.8425 | OK |
| Instab. DDD | 0,44 | Media (0.417+0.458+0.450+0.450)/4 = 0.444 | OK |
| Xenon DDD | 3/4 PASS | metrics-report: Catalogo DDD FAIL | OK |
| Xenon MVC | 4/4 PASS | metrics-report: todos PASS | OK |

### 2.7 Calculos no texto

| Afirmacao | Calculo | Status |
|-----------|---------|--------|
| "dispersao registrar monolito: 887→1445, aumento de 63%" | (1445-887)/887 = 62.9% | OK |
| "dispersao registrar micro: 1530→1734, aumento de 13%" | (1734-1530)/1530 = 13.3% | OK |
| "MVC 46% mais rapido na migracao" | (12:36-6:46)/12:36 = 46.3% | OK |
| "MVC ~3x mais rapido na construcao" | 24:50/8:00 = 3.1x | OK |
| "MVC 47% mais rapido feature mono" | (211-113)/211 = 46.4% | OK (~47%) |
| "MVC 47% mais rapido feature micro" | (181-95)/181 = 47.5% | OK |
| "diferenca absoluta bcrypt ~570ms" | 1530-887=643, 1460-917=543, media~593 | **MENOR: artigo diz ~570ms, calculo sugere ~590ms** |

**Resumo da verificacao de dados:** Todos os numeros do artigo correspondem aos dados-fonte, com excecao de duas discrepancias menores (1 segundo na soma da migracao DDD e ~20ms na estimativa de overhead do bcrypt). Nenhuma discrepancia critica.

---

## 3. Analise de diagramas

### 3.1 Diagramas existentes

| Arquivo | Conteudo | Relevante? | Secao sugerida | Titulo sugerido |
|---------|----------|-----------|----------------|-----------------|
| c4-context.png | Diagrama de contexto C4: Operador, Monolito, Microsservicos, SNS/SQS, Grafana | Sim | Material e Metodos (Dominio e modelagem) | Figura 1. Diagrama de contexto do sistema de gerenciamento de produtos e estoque |
| c4-container-monolith.png | Diagrama de container C4: camadas do monolito (Presentation→Application→Domain/Infrastructure→PostgreSQL) | Sim | Material e Metodos (Arquitetura) | Figura 2. Diagrama de "container" da arquitetura monolitica DDD |
| c4-container-microservices.png | Diagrama de container C4: microsservicos (API Gateway→Lambdas→DynamoDB, SNS→SQS) | Sim | Material e Metodos (Arquitetura) | Figura 3. Diagrama de "container" da arquitetura de microsservicos "serverless" DDD |
| sequence-create-product-monolith.png | Diagrama de sequencia: criacao de produto no monolito | Sim | Resultados e Discussao ou Material e Metodos | Figura 4. Diagrama de sequencia da criacao de produto no monolito |
| sequence-create-product-microservices.png | Diagrama de sequencia: criacao de produto em microsservicos com evento assincrono | Sim | Resultados e Discussao ou Material e Metodos | Figura 5. Diagrama de sequencia da criacao de produto nos microsservicos com comunicacao assincrona |
| sequence-stock-exit.png | Diagrama de sequencia: saida de estoque com invariante de saldo | Sim | Material e Metodos (Dominio e modelagem) | Figura 6. Diagrama de sequencia da saida de estoque com protecao de invariante do agregado |

**Recomendacao de priorizacao (limite de 30 paginas):** Os diagramas c4-container-monolith.png e c4-container-microservices.png sao os mais essenciais, pois ilustram a arquitetura discutida extensamente no artigo. O sequence-create-product-microservices.png e o mais rico, mostrando a comunicacao assincrona SNS/SQS. Sugere-se inserir ao menos 3 dos 6 diagramas (os dois containers e um de sequencia).

### 3.2 Diagramas ausentes que seriam uteis

| Diagrama sugerido | Relevancia | Prioridade |
|-------------------|-----------|------------|
| Grafico de barras: CC medio DDD vs MVC por codebase | Visualizaria a vantagem de CC do DDD de forma imediata. Poderia substituir parte do texto descritivo | Alta |
| Grafico de barras: IM medio DDD vs MVC por codebase | Mesmo raciocinio, especialmente para destacar a diferenca de 15,2 pontos no monolito | Alta |
| Grafico de barras: latencia p50 monolito vs microsservico por endpoint | Tornaria a comparacao visual mais impactante que a tabela | Media |
| Grafico de barras: tempos de implementacao por fase (DDD vs MVC) | Facilitaria a percepcao do trade-off velocidade vs qualidade | Media |
| Diagrama comparativo SLOC DDD vs MVC (empilhado por camada) | Mostraria como o DDD distribui codigo entre camadas enquanto MVC concentra | Baixa |

**Atencao:** Graficos de barra devem ser gerados em Excel (regra USP/ESALQ). Sem grade, sem borda, sem preenchimento. Eixos preto 1,5pt. Legendas nao em negrito.

---

## 4. Problemas encontrados

### CRITICOS (violariam regras USP/ESALQ — risco de reprovacao)

| # | Problema | Localizacao | Regra violada |
|---|----------|-------------|---------------|
| C1 | **Tempo verbal em Material e Metodos:** Diversas passagens usam presente do indicativo ("possui", "mantem", "conhece") em vez de preterito perfeito impessoal | Linha 164 (e possivelmente outras) | Item 2.6 pag. 16 do manual: "Verbos no preterito perfeito, forma impessoal" |
| C2 | **"et al." sem italico:** O termo latino "et al." aparece em texto normal em todas as 3 ocorrencias. Expressoes latinas devem estar em italico | Linhas 148, 215, 286 e possivelmente na Conclusao/Resumo | Regra de expressoes estrangeiras: "exceto latim = italico" |
| C3 | **Nome do orientador nao preenchido:** O campo de autoria diz "Nome do Orientador" em vez do nome real (Ugo Henrique Pereira da Silva) | Linha 63 | Dados obrigatorios da capa |
| C4 | **Enderecos dos autores nao preenchidos:** Placeholder generico em vez de enderecos reais | Linhas 65-67 | Dados obrigatorios da capa |
| C5 | **Nenhuma figura inserida no artigo:** O texto menciona 6 tabelas mas zero figuras. Existem 6 diagramas prontos em `docs/diagrams/` que nao foram inseridos. Os TODOs (linhas 180-184) indicam que figuras seriam adicionadas mas nao foram | Secao Material e Metodos | Regras de figuras (pag. 7-8) — embora nao seja obrigatorio ter figuras, a ausencia empobrece o artigo e os TODOs indicam intencao de inseri-las |

### IMPORTANTES (prejudicam clareza ou rigor academico)

| # | Problema | Localizacao | Impacto |
|---|----------|-------------|---------|
| I1 | **Numeracao de tabelas com lacuna:** O texto cita Tabela 2 a 6, mas nao existe Tabela 1 (so em TODO). Se Tabela 1 nao for inserida, as demais devem ser renumeradas 1 a 5 | Linhas 221-222 (TODO), 266 (1a referencia a Tabela 2) | Incoerencia na numeracao |
| I2 | **Expansao incorreta de SLOC:** O texto expande como "linhas de codigo executavel [SLOC]" mas SLOC = "Source Lines of Code". O acronimo ingles nao corresponde a traducao | Linha 230 | Imprecisao terminologica |
| I3 | **Titulo com "Serverless" maiusculo:** "Migração de monolito para microsserviços **S**erverless com Domain-Driven Design". A regra diz "so primeira palavra com maiuscula (exceto nomes proprios)". "Serverless" nao e nome proprio | Linhas 1 e 83 | Viola regra de formatacao do titulo |
| I4 | **Sobrenome do autor com "Dos" maiusculo:** "Gabriel Figueiredo **Dos** Santos". Em portugues, a particula "dos" e grafada em minuscula, exceto no inicio de frase | Linha 63 | Convencao onomastica |
| I5 | **Sigla CPU nao expandida:** "CPU" aparece entre aspas na linha 341 mas nunca e expandida | Linha 341 | Regra de siglas na 1a ocorrencia |
| I6 | **Agradecimento nao preenchido:** Contem placeholder "[PREENCHER SE DESEJADO]" | Linha 441 | Se nao houver agradecimento, remover a secao inteira |
| I7 | **Apendice nao preenchido:** Contem apenas comentarios TODO | Linhas 487-494 | Se nao houver apendice, remover a secao |
| I8 | **Ausencia de acentuacao no corpo do texto:** Todo o texto do corpo (Introducao, Material e Metodos, Resultados, Conclusao) esta sem acentos graficos (ex: "migracao" em vez de "migração", "codigo" em vez de "código"), enquanto o titulo, palavras-chave e comentarios HTML possuem acentos | Todo o corpo | Inconsistencia ortografica que deve ser resolvida na versao Word |

### MENORES (ajustes cosmeticos)

| # | Problema | Localizacao | Impacto |
|---|----------|-------------|---------|
| M1 | **Diferenca de 1 segundo na soma da migracao DDD:** Artigo diz 12min36s, soma dos servicos individuais (4:33+3:41+4:23) = 12min37s | Linha 234, Tabela 5 | Desprezivel |
| M2 | **Overhead bcrypt estimado como ~570ms:** Calculo real sugere ~590ms em media | Linha 341 | Estimativa aproximada, aceitavel com "~" |
| M3 | **Paragrafos longos na Conclusao:** Alguns paragrafos da Conclusao tem 100+ palavras. A regra recomenda "frases curtas" | Linhas 417-433 | Preferencia estilistica |
| M4 | **Cabecalho obrigatorio nao mencionado:** O artigo nao inclui o cabecalho "Trabalho de Conclusao de Curso apresentado para obtencao do titulo de especialista em..." | Todo o documento | Sera adicionado na versao Word |
| M5 | **Titulo em ingles como heading de secao:** "## Migration from monolith to Serverless microservices with Domain-Driven Design" esta como heading separado antes do Abstract. Na versao Word, deve ser titulo (nao secao) | Linha 83 | Formatacao Markdown vs Word |

---

## 5. Sugestoes de melhoria

### O que adicionar

1. **Inserir ao menos 3 figuras dos 6 diagramas disponiveis.** Prioridade:
   - Figura 1: c4-container-monolith.png (Material e Metodos)
   - Figura 2: c4-container-microservices.png (Material e Metodos)
   - Figura 3: sequence-create-product-microservices.png (Material e Metodos ou Resultados)

2. **Criar 1-2 graficos de barras** para Resultados e Discussao:
   - Grafico comparativo de IM medio DDD vs MVC por codebase (destaca a diferenca de 15 pontos no monolito)
   - Grafico comparativo de latencia p50 por endpoint (monolito vs microsservico)

3. **Inserir Tabela 1** (metricas coletadas, ferramentas e dimensoes) conforme o TODO existente, ou renumerar as tabelas existentes

4. **Preencher dados da capa:** nome do orientador, enderecos, email, nome do curso, ano da defesa

5. **Preencher ou remover** Agradecimento e Apendice

6. **Adicionar paragrafo de estrutura** ao final da Introducao (ex: "O artigo esta organizado em quatro secoes...")

### O que corrigir (prioridade)

1. Corrigir tempo verbal em Material e Metodos (preterito perfeito impessoal)
2. Colocar *et al.* em italico em todas as ocorrencias
3. Corrigir expansao de SLOC para "Source Lines of Code" [SLOC]
4. Corrigir "Serverless" para "serverless" no titulo
5. Corrigir "Dos" para "dos" no nome do autor
6. Expandir CPU na primeira ocorrencia
7. Resolver numeracao de tabelas (inserir Tabela 1 ou renumerar)
8. Adicionar acentuacao em todo o corpo do texto

### O que remover

1. Todos os comentarios TODO e blocos HTML de instrucoes (ao converter para Word)
2. Placeholder "[PREENCHER SE DESEJADO]" do Agradecimento
3. Linhas horizontais (---) que nao existem no formato Word

### O que reorganizar

1. Nenhuma reorganizacao estrutural necessaria. A ordem das secoes e subtopicos esta correta e segue o template USP/ESALQ.

---

## 6. Avaliacao geral

O artigo esta **substancialmente completo** e bem estruturado. O conteudo tecnico e solido, os dados sao verificaveis e consistentes com as fontes, e a argumentacao segue logica clara. Os principais riscos de reprovacao sao:

1. **Tempo verbal em Material e Metodos** — violacao direta de regra explicita
2. **Italico em *et al.*** — violacao de regra de expressoes latinas
3. **Dados da capa incompletos** — impede a entrega

Os demais problemas sao corrigiveis rapidamente. A qualidade da analise quantitativa, a verificacao cruzada dos dados e a cobertura das dimensoes propostas (qualidade, desempenho, produtividade) sao pontos fortes do trabalho.

**Estimativa de esforco para correcao:** 2-4 horas de trabalho para resolver todos os problemas criticos e importantes listados acima.
