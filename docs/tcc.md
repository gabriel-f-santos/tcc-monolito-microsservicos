# Migração de monolito para microsserviços Serverless com Domain-Driven Design

<!-- ============================================================
     REGRAS DE FORMATAÇÃO (MBA USP/ESALQ) — Aplicar ao passar para Word
     ============================================================

     GERAL:
     - Fonte: Arial 11 (texto), Arial 9 (endereço autores, notas de rodapé)
     - Margens: 2,5 cm (todas)
     - Espaçamento: 1,5 entre linhas (exceto resumo, rodapé, tabelas, títulos/fonte de figuras e tabelas = simples)
     - Espaçamento antes/depois: 0 pt
     - Cabeçalho/rodapé: posição 1,25 cm
     - Cabeçalho: "Trabalho de Conclusão de Curso apresentado para obtenção do título de especialista em (NOME DO CURSO) – (ANO DA DEFESA)"
     - Paginação: algarismos arábicos, canto inferior direito, Arial 9
     - Máximo: 30 páginas (incluindo apêndices/anexos)

     TÍTULO:
     - Negrito, centralizado
     - Só primeira palavra com maiúscula (exceto nomes próprios/científicos)
     - Máximo 15 palavras
     - Não pode ser alterado após entrega

     SEÇÕES:
     - Títulos de seção: negrito, alinhados à esquerda, sem recuo, sem numeração
     - Subtítulos: negrito, recuo especial 1,25 cm na primeira linha
     - Introdução: máx. 2 páginas, sem subtópicos, sem figuras/tabelas
     - Não existe seção separada de "Revisão de Literatura" — citações/contexto vão na Introdução

     FIGURAS:
     - Título ABAIXO da figura, justificado: "Figura X. Descrição sem ponto final"
     - Fonte abaixo do título: "Fonte: Dados originais da pesquisa" (sem ponto final)
     - Espaçamento simples, Arial 11
     - Gráficos de barra: sem grade, sem borda, sem preenchimento, eixos preto 1,5pt, legendas não em negrito
     - Gerar em Excel, nunca inserir como imagem

     TABELAS:
     - Título ACIMA da tabela: "Tabela X. Descrição sem ponto final"
     - Fonte abaixo: "Fonte: Resultados originais da pesquisa" (sem ponto final)
     - Usar ferramenta Tabela do Word/Excel (nunca imagem)
     - Sem cores, sem negrito no conteúdo
     - 1ª coluna: alinhada à esquerda; cabeçalhos: centralizados; números: à direita
     - Não ultrapassar margens

     CITAÇÕES:
     - Apenas citações INDIRETAS (com suas palavras, nunca cópia direta)
     - Até 2 autores: "Sobrenome1 e Sobrenome2 (ano)". 3+: "Sobrenome1 et al. (ano)"
     - Maiúscula só na primeira letra dos sobrenomes
     - Proibido apud — citar fonte original
     - Siglas: primeira ocorrência por extenso seguida de [SIGLA]

     REFERÊNCIAS:
     - Ordem alfabética, espaçamento simples, parágrafo simples entre entradas
     - Periódico: Autor(es). Ano. Título do trabalho. Nome da revista volume(edição): páginas.
     - Livro: Autor(es). Ano. Título. Edição. Editora, Cidade, Estado, País.

     EXPRESSÕES ESTRANGEIRAS:
     - Entre aspas (exceto latim = itálico)
     ============================================================ -->

<!-- TODO: Confirmar nome exato do curso (ex: "Digital Business", "Data Science and Analytics", etc.)
     e ano da defesa para preencher o cabeçalho -->

**Gabriel Figueiredo Dos Santos**$^{1*}$; **Nome do Orientador**$^{2}$

$^1$ Endereço profissional ou pessoal completo — Bairro; CEP Cidade, Estado, Brasil
$^2$ Endereço profissional ou pessoal completo — Bairro; CEP Cidade, Estado, Brasil
*autor correspondente: email@email.com

---

## Resumo

<!-- REGRA: Parágrafo único, espaçamento simples. Descrição geral do trabalho cobrindo todas as seções. -->
<!-- TODO: Redigir ao final, quando todos os resultados estiverem prontos. Deve cobrir: contexto, objetivo, metodologia, principais resultados e conclusão em um único parágrafo. -->

[PREENCHER AO FINAL — O resumo deve ser um único parágrafo cobrindo: (1) contexto do problema — monolitos vs. microsserviços "serverless", (2) objetivo — avaliar o impacto da migração usando DDD e "Clean Architecture", medindo qualidade, desempenho, custo e produtividade com ferramentas de IA, (3) metodologia — estudo de caso com duas versões do mesmo sistema, métricas de análise estática, testes de carga e medição de tempo com Claude Code e Codex, (4) principais resultados numéricos, (5) conclusão principal.]

**Palavras-chave:** microsserviços; "serverless"; "Domain-Driven Design"; análise estática; produtividade

---

<!-- Seção opcional -->
## Migration from monolith to Serverless microservices with Domain-Driven Design

## Abstract

[OPTIONAL — English version of Resumo]

**Keywords:** microservices; serverless; Domain-Driven Design; static analysis; productivity

---

## Introducao

<!-- ================================================================
     REGRAS DESTA SEÇÃO:
     - Máximo 2 páginas
     - SEM subtópicos
     - SEM figuras ou tabelas
     - Contextualização apoiada em citações bibliográficas
     - Justificativa e objetivos da pesquisa inseridos aqui
     - NÃO existe seção separada de Revisão de Literatura
     ================================================================ -->

<!-- TODO: Esta seção precisa ser redigida com referências bibliográficas reais.
     Estrutura sugerida para os parágrafos:

     §1 — CONTEXTO: A crescente adoção de arquiteturas distribuídas em substituição a monolitos.
           Citar: Newman (2021) "Building Microservices", Fowler (2014) sobre "Microservices".
           Mencionar o crescimento de "serverless" (AWS Lambda) como modelo de implantação.

     §2 — PROBLEMA: A migração de monolito para microsserviços introduz desafios:
           acoplamento entre serviços, duplicação de modelos, custos ocultos (NAT Gateway,
           observabilidade, CI/CD). Citar: Vernon (2016) "Domain-Driven Design Distilled",
           Evans (2003) "Domain-Driven Design: Tackling Complexity".
           DDD oferece ferramentas conceituais (Bounded Contexts, Aggregates) para definir
           fronteiras, mas a literatura raramente demonstra isso com métricas quantitativas.

     §3 — LACUNA E JUSTIFICATIVA: Estudos existentes comparam monolitos e microsserviços
           com métricas superficiais (LOC, número de arquivos). Faltam análises com:
           complexidade ciclomática, índice de manutenibilidade, percentis de latência (p95/p99),
           e medição objetiva do esforço de desenvolvimento.
           Além disso, o uso de assistentes de IA (Claude Code, Codex) como instrumento de
           medição de produtividade é um campo ainda pouco explorado.

     §4 — OBJETIVO: Este trabalho tem como objetivo avaliar quantitativamente o impacto da
           migração de um sistema monolítico para microsserviços "serverless", utilizando
           Domain-Driven Design e Clean Architecture, por meio de métricas de qualidade de
           código, desempenho, custo operacional e produtividade assistida por IA.

     §5 — ESTRUTURA: Breve descrição do que cada seção contém.

     REFERÊNCIAS SUGERIDAS PARA BUSCAR:
     - Evans, E. 2003. Domain-Driven Design: Tackling Complexity in the Heart of Software.
     - Vernon, V. 2016. Domain-Driven Design Distilled.
     - Newman, S. 2021. Building Microservices. 2ed.
     - Martin, R.C. 2017. Clean Architecture.
     - Fowler, M. 2014. Microservices (artigo online — verificar se aceito como referência).
     - Roberts, M.; Chapin, J. 2017. What is Serverless? O'Reilly.
     - Estudos sobre métricas de software: McCabe (1976) complexidade ciclomática,
       Halstead (1977), índice de manutenibilidade (Oman e Hagemeister, 1992).
-->

[PREENCHER COM REFERENCIAS — Redigir em até 2 páginas seguindo a estrutura dos parágrafos acima.]

---

## Material e Metodos

<!-- ================================================================
     REGRAS DESTA SEÇÃO:
     - Pode ter subtópicos (negrito, recuo 1,25cm)
     - Descrição detalhada da metodologia
     - Não mencionar nome de empresa/instituição — usar localização geográfica
     - Fonte de dados da pesquisa: "Dados originais da pesquisa"
     ================================================================ -->

Este trabalho adota uma abordagem de estudo de caso com duas implementacoes do mesmo sistema de gerenciamento de produtos e estoque: uma versao monolitica e uma versao baseada em microsservicos "serverless". Ambas compartilham a mesma especificacao de dominio e os mesmos casos de uso, diferindo apenas nas camadas de apresentacao e infraestrutura. As metricas foram coletadas de forma sistematica ao longo do processo de desenvolvimento e em testes controlados apos a implantacao.

**Dominio e modelagem**

O sistema foi modelado seguindo os principios de "Domain-Driven Design" [DDD] (Evans, 2003), com dois "Bounded Contexts" [BC] claramente delimitados: Catalogo de Produtos e Controle de Estoque. A Linguagem Ubiqua foi formalizada em um glossario com nove termos fundamentais: Produto, SKU [Stock Keeping Unit], Categoria, Item de Estoque, Movimentacao, Entrada, Saida, Saldo e Lote.

O contexto de Catalogo possui como raiz de agregacao a entidade Produto, composta por "Value Objects" imutaveis (SKU e Dinheiro) e referencia a entidade Categoria. O contexto de Estoque possui como raiz de agregacao o Item de Estoque, que mantem um saldo calculado a partir de entidades de Movimentacao (Entrada ou Saida). O Estoque nao conhece o dominio de Catalogo diretamente — mantem apenas uma projecao local com dados minimos (SKU, nome, categoria) recebidos por meio de eventos assincronos.

A comunicacao entre contextos ocorre exclusivamente via eventos de dominio publicados em topico SNS ["Simple Notification Service"] e consumidos por fila SQS ["Simple Queue Service"], garantindo desacoplamento total e consistencia eventual. Os eventos definidos sao: ProdutoCriado, ProdutoAtualizado e ProdutoDesativado (emitidos pelo Catalogo) e EstoqueMovimentado e EstoqueInsuficiente (emitidos pelo Estoque).

**Arquitetura e decisoes tecnicas**

Ambas as versoes seguem "Clean Architecture" (Martin, 2017) com **organizacao por dominio**: o codigo e estruturado em modulos correspondentes aos "Bounded Contexts" [BC] do DDD, e nao em camadas horizontais. Cada modulo (auth, catalogo, estoque) contem suas proprias quatro camadas internas: dominio (agregados, entidades, "value objects", interfaces de repositorio), aplicacao (casos de uso), infraestrutura (implementacoes de repositorio) e apresentacao (controladores HTTP ou "handlers" Lambda). Um modulo compartilhado ("shared") fornece as abstracoes base (entidade, excecao, repositorio) e configuracao de infraestrutura.

Essa organizacao oferece tres vantagens mensuráveis: (1) cada "Bounded Context" e autocontido, podendo ser extraido como microsservico copiando-se a pasta; (2) imports entre modulos sao explicitos — a fronteira logica do DDD se materializa como fronteira fisica no sistema de arquivos; (3) metricas de qualidade podem ser coletadas por modulo individualmente (por exemplo, complexidade ciclomatica apenas do modulo de estoque).

A versao monolitica utiliza o "framework" FastAPI com rotas HTTP que delegam aos casos de uso, repositorios implementados com SQLAlchemy sobre PostgreSQL, e execucao em servidor ASGI ["Asynchronous Server Gateway Interface"] convencional. O container Docker e limitado a 512MB de memoria, equivalente a configuracao das funcoes Lambda.

A versao em microsservicos utiliza "handlers" AWS Lambda puros (sem adaptador Mangum), onde cada funcao Lambda recebe o evento do API Gateway e delega ao mesmo caso de uso. Os repositorios sao implementados com a biblioteca boto3 sobre DynamoDB. Essa decisao arquitetural — Lambda puro em vez de adaptador — foi intencional para demonstrar que a camada de aplicacao (casos de uso) e genuinamente agnostica ao mecanismo de transporte. O mesmo caso de uso funciona identicamente quando chamado por uma rota FastAPI ou por um "handler" Lambda.

A troca de PostgreSQL (monolito) para DynamoDB (microsservicos) demonstra na pratica o "Repository Pattern": a interface de repositorio definida no dominio permanece identica, e apenas a implementacao de infraestrutura muda. Essa decisao tambem elimina a necessidade de NAT Gateway na AWS, reduzindo custos operacionais.

A injecao de dependencia foi implementada com a biblioteca "dependency-injector", utilizando o padrao de "Composition Root" [CR]: cada "Bounded Context" possui um container declarativo (DeclarativeContainer) que e o unico ponto do sistema que conhece as implementacoes concretas dos repositorios. Os casos de uso recebem interfaces via construtor e desconhecem se estao conectados a PostgreSQL, DynamoDB ou repositorios em memoria (usados em testes). A biblioteca oferece provedores tipados (Factory, Singleton, Configuration) e um mecanismo de "override" que permite substituir implementacoes em testes sem alterar codigo de producao. Essa abordagem foi preferida ao mecanismo Depends() do FastAPI por nao acoplar a composicao de dependencias ao "framework", mantendo as camadas de dominio e aplicacao como Python puro — requisito fundamental da "Clean Architecture".

<!-- TODO: Adicionar diagrama da arquitetura como Figura ao passar para Word.
     Figura 1. Arquitetura do sistema monolitico
     Figura 2. Arquitetura dos microsservicos "serverless"
     Figura 3. Fluxo de eventos entre "Bounded Contexts"
     Fonte: Dados originais da pesquisa -->

**Ferramentas e tecnologias**

As principais tecnologias utilizadas foram:

- Linguagem: Python 3.12
- "Framework" HTTP (monolito): FastAPI
- Computacao "serverless": AWS Lambda com API Gateway
- Banco de dados: PostgreSQL 16 (monolito) e DynamoDB (microsservicos)
- Mensageria: Amazon SNS e SQS
- Infraestrutura como codigo: AWS SAM ["Serverless Application Model"]
- Integracao continua: GitHub Actions
- Analise estatica: radon (complexidade ciclomatica) e xenon ("thresholds" de qualidade)
- Testes de carga: k6
- Observabilidade: Grafana Cloud (free tier), OpenTelemetry, AWS X-Ray

**Metricas coletadas**

Para avaliar a migracao de forma quantitativa, foram definidas metricas em quatro dimensoes:

*Qualidade de codigo:* complexidade ciclomatica (McCabe, 1976) medida com a ferramenta radon, que atribui graus de A (baixa complexidade) a F (alta complexidade) a cada funcao; e indice de manutenibilidade, calculado a partir de uma combinacao de volume de Halstead, complexidade ciclomatica e linhas de codigo, em escala de 0 a 100.

*Desempenho:* latencia nos percentis p50, p95 e p99; "throughput" (requisicoes por segundo); e duracao de "cold starts" (primeira invocacao apos periodo ocioso). Os testes de carga foram executados com k6 em tres cenarios: carga constante (50 requisicoes por segundo durante 2 minutos), "burst" (0 a 200 requisicoes por segundo em 10 segundos) e rampa gradual (10 a 100 requisicoes por segundo em 5 minutos).

*Custo operacional:* custo real extraido do painel de faturamento da AWS apos execucao dos testes, com projecoes para diferentes padroes de carga (baixa, media, alta).

*Produtividade com IA:* cada funcionalidade foi implementada separadamente utilizando Claude Code e Codex. Para cada implementacao foi registrado: tempo total do prompt ate codigo funcional (em minutos), numero de iteracoes de correcao ate os testes passarem, tamanho do "diff" gerado (linhas adicionadas e removidas), e variacao na complexidade ciclomatica e indice de manutenibilidade antes e depois da feature.

<!-- TODO: Inserir Tabela ao passar para Word:
     Tabela 1. Metricas coletadas, ferramentas e dimensoes de avaliacao
     Colunas: Dimensao | Metrica | Ferramenta | Unidade
     Fonte: Dados originais da pesquisa -->

**Procedimento experimental**

O desenvolvimento seguiu uma estrategia de "Walking Skeleton": toda a infraestrutura (CI/CD, observabilidade, bancos de dados, filas) foi provisionada e validada antes de qualquer implementacao de logica de negocio, contendo apenas um "endpoint" de verificacao de saude (/health). Essa abordagem isola o tempo de configuracao de infraestrutura do tempo de desenvolvimento de funcionalidades, permitindo medicao precisa da produtividade.

As funcionalidades foram adicionadas incrementalmente na seguinte ordem: (1) CRUD de Produto, (2) entrada de estoque, (3) saida de estoque, (4) evento ProdutoCriado com projecao no Estoque, (5) categoria de produto com filtro de estoque por categoria. Cada funcionalidade foi implementada quatro vezes: monolito com Claude Code, monolito com Codex, microsservicos com Claude Code, e microsservicos com Codex.

<!-- TODO: Inserir Tabela ao passar para Word:
     Tabela 2. Planilha de coleta de metricas de produtividade com IA
     Colunas: Feature | Arquitetura | Ferramenta IA | Tempo (min) | Iteracoes | Diff (linhas) | CC antes | CC depois | MI antes | MI depois
     Fonte: Dados originais da pesquisa -->

---

## Resultados e Discussao

<!-- ================================================================
     REGRAS DESTA SEÇÃO:
     - Pode ter subtópicos (negrito, recuo 1,25cm)
     - Apresentar resultados E interpretar/discutir
     - Figuras: título abaixo, "Fonte: Resultados originais da pesquisa"
     - Tabelas: título acima, "Fonte: Resultados originais da pesquisa"
     ================================================================ -->

<!-- TODO: Esta seção será preenchida após a implementação e coleta de dados (Fases 5-7 do plano).
     Estrutura planejada dos subtópicos: -->

**Modelagem e estrutura do dominio**

<!-- TODO: Apresentar como o DDD foi aplicado na prática.
     - Mostrar trechos de código dos Aggregates, Value Objects, interfaces de Repository
     - Comparar a estrutura do monolito e microsserviços
     - Discutir como a projeção local no Estoque eliminou o acoplamento síncrono
     - Figura: diagrama de agregados e eventos
     Fonte: Resultados originais da pesquisa -->

[PREENCHER APOS IMPLEMENTACAO]

**Qualidade de codigo e manutenibilidade**

<!-- TODO: Apresentar resultados do radon (CC e MI).
     - Tabela comparativa: monolito vs microsserviços, por módulo/função
     - Discutir se a separação em microsserviços aumentou ou reduziu complexidade
     - Analisar impacto do Repository Pattern na manutenibilidade
     - Comparar com valores de referência da literatura (CC <= 10 = aceitável, MI >= 65 = bom)
     Fonte: Resultados originais da pesquisa -->

[PREENCHER APOS IMPLEMENTACAO]

**Desempenho e latencia**

<!-- TODO: Apresentar resultados do k6.
     - Tabela com p50, p95, p99 e throughput para cada cenário e cada arquitetura
     - Gráficos do Grafana mostrando distribuição de latência
     - Análise específica de cold starts: frequência, duração, impacto no p99
     - Discutir em quais cenários de carga cada arquitetura se sai melhor
     Fonte: Resultados originais da pesquisa -->

[PREENCHER APOS TESTES DE CARGA]

**Custo operacional**

<!-- TODO: Apresentar custos reais da AWS.
     - Tabela comparativa: monolito (EC2/ECS 24h) vs microsserviços (Lambda + DynamoDB)
     - Discutir: eliminação do NAT Gateway com DynamoDB
     - Projeções para cenários de carga real (esporádica, constante, picos)
     - Custos ocultos: CI/CD, monitoramento, debugging distribuído
     Fonte: Resultados originais da pesquisa -->

[PREENCHER APOS ANALISE DE CUSTOS]

**Produtividade assistida por inteligencia artificial**

<!-- TODO: Apresentar resultados da medição com Claude Code e Codex.
     - Tabela completa com todas as features x arquiteturas x ferramentas
     - Análise: a IA foi mais rápida no monolito ou nos microsserviços?
     - Quantas iterações de correção foram necessárias em cada caso?
     - Discutir: a arquitetura impacta a produtividade da IA?
     - Discutir: a especificação DDD (spec.md) ajudou a IA a gerar código mais preciso?
     Fonte: Resultados originais da pesquisa -->

[PREENCHER APOS MEDICOES COM IA]

**Discussao geral e limitacoes**

<!-- TODO: Síntese cruzando todas as dimensões.
     - Em quais cenários a migração se justifica?
     - Trade-offs: ganho em desacoplamento vs. custo de complexidade operacional
     - Limitações metodológicas: sistema de domínio simples, escala reduzida,
       medição de tempo com IA depende do prompt e do estado do modelo
     - Discutir viés: o mesmo desenvolvedor implementou ambas as versões
-->

[PREENCHER AO FINAL]

---

## Conclusao

<!-- ================================================================
     REGRAS DESTA SEÇÃO:
     - Frases curtas com conclusões/inferências dos resultados
     - Sem restrição de tamanho, mas recomenda-se ser sucinta
     - SEM tabelas ou figuras
     ================================================================ -->

<!-- TODO: Redigir ao final com base nos resultados. Deve conter:
     - Resposta ao objetivo: a migração melhorou/piorou qualidade, desempenho, custo?
     - O DDD e Clean Architecture facilitaram a migração? O Repository Pattern funcionou?
     - A comunicação assíncrona resolveu o problema de acoplamento?
     - A IA foi mais produtiva em qual arquitetura?
     - Limitações: domínio simples, escala de testes, variabilidade das ferramentas de IA
     - Trabalhos futuros: chaos engineering, escala maior, outros domínios, outros modelos de IA
-->

[PREENCHER AO FINAL]

---

## Agradecimento

<!-- Opcional, máximo 3 linhas -->

[PREENCHER SE DESEJADO]

---

## Referencias

<!-- ================================================================
     REGRAS:
     - Ordem alfabética
     - Espaçamento simples, parágrafo simples entre entradas
     - Apenas citações indiretas no texto
     - Formato periódico: Autor(es). Ano. Título. Nome da revista volume(edição): páginas.
     - Formato livro: Autor(es). Ano. Título. Edição. Editora, Cidade, Estado, País.
     - Proibido apud
     ================================================================ -->

<!-- TODO: Preencher conforme as citações forem adicionadas ao texto.
     Referências prováveis (verificar edição, editora e dados completos):

Evans, E. 2003. Domain-Driven Design: Tackling Complexity in the Heart of Software. 1ed. Addison-Wesley, Boston, MA, USA.

Martin, R.C. 2017. Clean Architecture: A Craftsman's Guide to Software Structure and Design. 1ed. Prentice Hall, Upper Saddle River, NJ, USA.

McCabe, T.J. 1976. A complexity measure. IEEE Transactions on Software Engineering SE-2(4): 308-320.

Newman, S. 2021. Building Microservices: Designing Fine-Grained Systems. 2ed. O'Reilly Media, Sebastopol, CA, USA.

Vernon, V. 2016. Domain-Driven Design Distilled. 1ed. Addison-Wesley, Boston, MA, USA.

[Adicionar demais referências conforme citadas no texto]
-->

---

## Apendice

<!-- Opcional — material complementar elaborado pelo autor -->

<!-- Possíveis apêndices:
     A. Especificação completa do domínio (spec.md)
     B. Contratos de API detalhados
     C. Resultados completos dos testes de carga (k6)
     D. Logs de sessão com Claude Code e Codex (evidência das medições)
-->
