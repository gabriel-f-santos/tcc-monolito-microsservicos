# Metricas do TCC — Definicoes, Ferramentas e Referencias

## Mapa: metrica → ferramenta → como usamos

| Metrica | Ferramenta | Versao | Comando / Funcao | O que mede |
|---------|-----------|--------|-----------------|------------|
| **CC** (Complexidade Ciclomatica) | `radon` | 6.0.1 | `radon cc -s -a <path>` | Caminhos independentes no fluxo de controle por funcao/metodo. Media por codebase. |
| **MI** (Maintainability Index) | `radon` | 6.0.1 | `radon mi -s <path>` | Indice composto (Halstead + CC + LOC), escala 0-100. Media por codebase. |
| **LOC / SLOC** | `radon` | 6.0.1 | `radon raw -s <path>` | Linhas de codigo total (LOC) e executavel (SLOC). |
| **Halstead** (Volume, Dificuldade, Esforco) | `radon` | 6.0.1 | `radon hal <path>` | Metricas baseadas em operadores/operandos: tamanho informacional, esforco cognitivo. |
| **Xenon** (Gate de qualidade) | `xenon` | 0.9.3 | `xenon --max-absolute C --max-modules B --max-average A <path>` | Fail/pass binario com thresholds de CC. Usado como fitness function. |
| **Ca / Ce / I** (Acoplamento Aferente/Eferente e Instabilidade) | `grimp` | 3.14 | Script `measure_quality.py` → `compute_coupling()` | Constroi grafo de imports, agrupa por pacote (2 niveis), calcula Ca, Ce e `I = Ce/(Ca+Ce)`. |
| **Coesao** (LCOM invertido) | `cohesion` | 1.2.0 | `cohesion -d <path>` | % de atributos da classe acessados pelos metodos. 100% = totalmente coeso. |
| **Tempo de implementacao** | `migration-timer.sh` | proprio | `bash scripts/migration-timer.sh start/end <name>` | Grava `date +%s.%N` em start/end, calcula delta em `metrics/migration-times/summary.csv`. |

---

## Detalhamento por metrica

### 1. Complexidade Ciclomatica (CC)

**Definicao**: numero de caminhos linearmente independentes no grafo de fluxo de controle. `CC = pontos de decisao + 1`.

**Formula**: `V(G) = E - N + 2P` (arestas - nos + 2 × componentes conexos)

**Escala**: A(1-5) simples | B(6-10) moderada | C(11-20) complexa | D(21+) muito complexa

**Ferramenta**: `radon cc -s -a` → analisa cada funcao/metodo, classifica A-F, reporta media.

**Como usamos**: rodamos em cada um dos 8 codebases (2 monolitos + 6 microsservicos). O script `measure_quality.py` parseia a saida e extrai `avg_cc` e `blocks` (total de funcoes analisadas). Usamos para comparar DDD vs MVC: DDD CC medio ~2.09, MVC ~3.07.

**Referencia**: McCABE, T. J. A Complexity Measure. *IEEE Transactions on Software Engineering*, v. SE-2, n. 4, p. 308-320, 1976.

---

### 2. Maintainability Index (MI)

**Definicao**: indice composto que combina Volume de Halstead, CC e LOC. Escala 0-100 (radon normaliza via `max(0, MI × 100/171)`).

**Formula**: `MI = 171 - 5.2·ln(avgHV) - 0.23·avgCC - 16.2·ln(avgLOC)`

**Escala**: >85 alta | 65-85 moderada | <65 baixa (candidato a refatoracao)

**Ferramenta**: `radon mi -s` → classifica cada arquivo A-C com score numerico. O script parseia e calcula media.

**Como usamos**: MI medio por codebase. DDD monolito 90.28 vs MVC 75.04 — DDD significativamente mais manutenivel. Microsservicos convergem mais (DDD ~87 vs MVC ~84).

**Referencias**:
- OMAN, P.; HAGEMEISTER, J. Metrics for Assessing a Software System's Maintainability. *ICSM'92*, IEEE, 1992.
- COLEMAN, D. et al. Using Metrics to Evaluate Software System Maintainability. *Computer*, v. 27, n. 8, 1994.

---

### 3. Halstead (Volume, Dificuldade, Esforco)

**Definicao**: metricas baseadas em contagem de operadores (n1/N1) e operandos (n2/N2) distintos e totais.

**Formulas**: Volume `V = N·log2(n)` | Dificuldade `D = (n1/2)·(N2/n2)` | Esforco `E = D·V`

**Ferramenta**: `radon hal` → reporta por funcao. Saida bruta salva em `metrics/raw/<codebase>/radon-hal.txt`.

**Como usamos**: como componente do MI (nao reportamos Halstead isolado nas tabelas do TCC, mas o valor alimenta o calculo do MI). Saida bruta disponivel para auditoria.

**Referencia**: HALSTEAD, M. H. *Elements of Software Science*. New York: Elsevier, 1977.

---

### 4. Acoplamento Aferente (Ca) e Eferente (Ce)

**Definicao**: Ca = quantos pacotes dependem deste. Ce = de quantos pacotes este depende.

**Ferramenta**: `grimp` (constroi grafo de imports Python). O script `measure_quality.py` chama `grimp.build_graph()`, agrupa modulos por pacote de 2 niveis (ex: `src.auth`, `src.domain`), e conta dependencias entre pacotes usando `find_modules_directly_imported_by` / `find_modules_that_directly_import`.

**Como usamos**: monolito DDD tem 6 pacotes com dependencias direcionais (handler→app→domain→shared). MVC tem 1-4 pacotes sem dependencias internas (cada route e ilha). Microsservicos DDD tem 5-6 pacotes; MVC tem 1.

**Referencia primaria**: MARTIN, R. C. OO Design Quality Metrics: An Analysis of Dependencies. *Object Mentor*, 1994.

**Nos livros do TCC**:
- RICHARDS, M.; FORD, N. *Fundamentals of Software Architecture*. O'Reilly, 2020. **Cap. 3 (Modularity)**: explica Ca/Ce como base para instabilidade.
- FORD, N. et al. *Software Architecture: The Hard Parts*. O'Reilly, 2022: usa Ca/Ce para decidir onde cortar monolito.

---

### 5. Instabilidade (I)

**Definicao**: suscetibilidade a mudancas. `I = Ce / (Ca + Ce)`. 0 = estavel, 1 = instavel.

**Escala**: 0.0-0.3 estavel | 0.3-0.7 equilibrio | 0.7-1.0 instavel

**Ferramenta**: calculada no `measure_quality.py` a partir de Ca/Ce do grimp.

**Como usamos**: instabilidade media por codebase. DDD ~0.45 (dependencias direcionais corretas). MVC 0.00 (pacote unico, nada a medir).

**Referencia**: MARTIN, R. C. *Agile Software Development: Principles, Patterns, and Practices*. Prentice Hall, 2003. Cap. 20. Tambem: *Clean Architecture*, 2017, Cap. 14.

**Nos livros do TCC**:
- RICHARDS; FORD (2020) Cap. 3: formula + diagrama da sequencia principal.
- FORD et al. (2022): instabilidade usada para priorizar componentes na migracao monolito→microsservicos.

---

### 6. Coesao (LCOM invertido)

**Definicao**: grau em que metodos de uma classe acessam os mesmos atributos. A ferramenta `cohesion` reporta percentual: 100% = todo metodo acessa todo atributo (totalmente coeso), 0% = nenhuma sobreposicao.

**Nota**: e o inverso do LCOM classico de Chidamber-Kemerer. `cohesion` calcula `(metodos que acessam atributo / total de metodos)` por atributo e faz media.

**Ferramenta**: `cohesion -d <path>` → lista classes com % de coesao por metodo e total.

**Como usamos**: so mensuravel em DDD (que tem classes — entidades, agregados, VOs). MVC tem 0 classes (tudo funcao). DDD monolito: 87 classes, coesao media 32%. Microsservicos DDD: 18-28 classes, coesao 28-49%.

**Referencia**: CHIDAMBER, S. R.; KEMERER, C. F. A Metrics Suite for Object Oriented Design. *IEEE Transactions on Software Engineering*, v. 20, n. 6, 1994.

**Nos livros do TCC**:
- RICHARDS; FORD (2020) Cap. 3: tipos de coesao como pilar de modularidade.
- FORD et al. (2022): coesao como criterio para fronteiras de servicos.

---

### 7. Linhas de Codigo (LOC / SLOC)

**Definicao**: LOC = todas as linhas; SLOC = so linhas executaveis (sem brancos/comentarios).

**Ferramenta**: `radon raw -s` → reporta LOC, LLOC, SLOC, comentarios, brancos, por arquivo e total.

**Como usamos**: SLOC por codebase para comparar tamanho DDD vs MVC. DDD ~3x mais SLOC que MVC (monolito: 1821 vs 466; microsservicos: ~568 vs ~200 media). Tambem alimenta o MI.

**Referencia**: JONES, C. *Applied Software Measurement*. 3 ed. McGraw-Hill, 2008.

---

### 8. Tempo de implementacao

**Definicao**: tempo de parede (wall clock) entre inicio e fim da implementacao por um agente de IA.

**Ferramenta**: script proprio `scripts/migration-timer.sh`. Grava `date +%s.%N` em arquivos `metrics/migration-times/<service>.start` e `.end`, calcula delta em `summary.csv`.

**Como usamos**: cada subagente Claude Code executa `timer start` como primeira acao e `timer end` como ultima. Resultados: DDD ~2x mais lento que MVC na migracao (12.6min vs 6.8min somado), ~1.9x na feature (3min31s vs 1min53s monolito).

**Referencia**: nao ha referencia academica especifica para cronometragem de agentes IA. Pode-se citar como "medicao de tempo de desenvolvimento assistido por IA" e referenciar o conceito de *development velocity* de:
- FORSGREN, N.; HUMBLE, J.; KIM, G. *Accelerate: The Science of Lean Software and DevOps*. IT Revolution, 2018. (metricas DORA de lead time)

---

## Xenon (gate de qualidade)

**Definicao**: ferramenta que aplica thresholds de CC e falha se qualquer funcao, modulo ou media ultrapassa o limite. Funciona como *fitness function* arquitetural.

**Ferramenta**: `xenon --max-absolute C --max-modules B --max-average A` → exit 0 (PASS) ou exit 1 (FAIL).

**Como usamos**: PASS/FAIL binario por codebase. 7 de 8 passam; catalogo-service DDD FAIL (tem funcao com CC nivel B+, handler de roteamento).

**Referencia para fitness functions**:
- RICHARDS; FORD (2020) **Cap. 6**: architectural fitness functions como testes automatizados de propriedades arquiteturais.

---

## Resumo de ferramentas

| Ferramenta | Tipo | Metricas | Instalacao |
|-----------|------|---------|-----------|
| `radon` 6.0.1 | CLI Python | CC, MI, LOC/SLOC, Halstead | `pip install radon` |
| `xenon` 0.9.3 | CLI Python (wrapper radon) | Gate CC (pass/fail) | `pip install xenon` |
| `grimp` 3.14 | Lib Python | Grafo de imports → Ca/Ce/I | `pip install grimp` |
| `cohesion` 1.2.0 | CLI Python | LCOM invertido por classe | `pip install cohesion` |
| `pydeps` 3.0.2 | CLI Python | Visualizacao de dependencias (SVG) | `pip install pydeps` (instalado mas nao usado no report) |
| `migration-timer.sh` | Script bash proprio | Tempo de implementacao | N/A |
| `measure_quality.py` | Script Python proprio | Orquestrador que roda todas as acima | N/A |

**Nota**: `pydeps` esta instalado mas nao foi usado no relatorio final. Pode ser usado para gerar diagramas SVG de dependencia para o artigo.
