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

A migracao de sistemas monoliticos para microsservicos e uma tendencia consolidada na engenharia de software, porem frequentemente avaliada com metricas superficiais. Este trabalho teve como objetivo avaliar quantitativamente o impacto da migracao de um monolito para microsservicos serverless utilizando Domain-Driven Design e Clean Architecture, por meio de metricas de qualidade de codigo, desempenho e produtividade assistida por inteligencia artificial. Adotou-se um estudo de caso experimental com quatro implementacoes do mesmo sistema de catalogo e estoque — monolito DDD, monolito MVC (grupo de controle) e suas respectivas migracoes para AWS Lambda — totalizando oito bases de codigo. As metricas de complexidade ciclomatica, indice de manutenibilidade, acoplamento entre pacotes e latencia foram coletadas com ferramentas de analise estatica (radon, grimp) e testes de carga (k6). O DDD produziu codigo com complexidade ciclomatica 27% menor e indice de manutenibilidade 6,3 pontos superior ao MVC na media global, com diferenca de 15,2 pontos no monolito (90,28 contra 75,04). Os microsservicos apresentaram latencia duas a tres vezes maior que o monolito no percentil 50, porem com dispersao menor entre p50 e p95, indicando maior previsibilidade. O MVC foi entre 46% e tres vezes mais rapido em todas as fases de desenvolvimento. Todas as doze implementacoes por agente de IA convergiram na primeira iteracao com 100% dos testes aprovados. Conclui-se que o DDD oferece vantagens estruturais mensuraveis em manutenibilidade e modularidade, enquanto o MVC oferece maior velocidade de entrega, configurando um trade-off dependente da complexidade do dominio e do horizonte de evolucao do sistema.

**Palavras-chave:** microsserviços; "serverless"; "Domain-Driven Design"; análise estática; produtividade

---

<!-- Seção opcional -->
## Migration from monolith to Serverless microservices with Domain-Driven Design

## Abstract

Migrating monolithic systems to microservices is a well-established trend in software engineering, yet it is frequently assessed using superficial metrics. This study aimed to quantitatively evaluate the impact of migrating a monolith to serverless microservices using Domain-Driven Design and Clean Architecture, measuring code quality, performance, and AI-assisted productivity. An experimental case study was conducted with four implementations of the same product catalog and inventory system — a DDD monolith, an MVC monolith (control group), and their respective migrations to AWS Lambda — totaling eight codebases. Cyclomatic complexity, maintainability index, package coupling, and latency metrics were collected using static analysis tools (radon, grimp) and load testing (k6). DDD produced code with 27% lower cyclomatic complexity and a maintainability index 6.3 points higher than MVC on a global average, with a 15.2-point difference in the monolith (90.28 versus 75.04). Microservices exhibited two to three times higher latency than the monolith at the 50th percentile, yet showed lower dispersion between p50 and p95, indicating greater predictability. MVC was between 46% and three times faster across all development phases. All twelve AI agent implementations converged on the first iteration with 100% of tests passing. It is concluded that DDD provides measurable structural advantages in maintainability and modularity, while MVC offers faster delivery speed, resulting in a trade-off dependent on domain complexity and the system's expected evolution horizon.

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

A adocao de arquiteturas baseadas em microsservicos tem se consolidado como alternativa ao modelo monolitico tradicional em organizacoes que buscam escalabilidade independente, ciclos de implantacao mais curtos e autonomia entre equipes. Newman (2021) descreve microsservicos como servicos independentemente implantaveis, modelados em torno de um dominio de negocio, que se comunicam por meio de interfaces bem definidas. Em paralelo, o modelo de computacao "serverless", no qual o provedor de nuvem gerencia a infraestrutura de execucao e cobra apenas pelo tempo efetivo de processamento, tem reduzido a barreira operacional para a implantacao de arquiteturas distribuidas. Richards e Ford (2020) argumentam que decisoes arquiteturais devem ser orientadas por metricas objetivas — como acoplamento, coesao e modularidade — e nao apenas por preferencias tecnologicas, o que reforça a necessidade de avaliacoes quantitativas na comparacao entre estilos arquiteturais.

O Domain-Driven Design [DDD], proposto por Evans (2003), oferece ferramentas conceituais para lidar com a complexidade inerente a sistemas de software, entre as quais se destacam os Contextos Delimitados [do ingles "Bounded Contexts"], os Agregados e a Linguagem Ubiqua. Essas abstraccoes permitem definir fronteiras explicitas entre subdominios de negocio, o que se traduz naturalmente em limites de servicos quando da adocao de microsservicos. Vernon (2013) detalha a aplicacao pratica dessas construcoes, demonstrando como Contextos Delimitados podem encapsular modelos autonomos com regras de negocio independentes. A "Clean Architecture", sistematizada por Martin (2017), complementa o DDD ao estabelecer a regra de dependencia — na qual camadas externas dependem das internas, mas nunca o contrario —, promovendo o desacoplamento entre logica de dominio e detalhes de infraestrutura. Percival e Gregory (2020) demonstram a aplicacao conjunta do "Repository Pattern" e da inversao de dependencia em Python, viabilizando a substituicao de tecnologias de persistencia sem alteracao nas camadas de dominio e aplicacao.

Apesar dos beneficios teoricos, a migracao de um monolito para microsservicos introduz desafios concretos. Newman (2019) cataloga riscos recorrentes nesse processo, incluindo acoplamento entre servicos, duplicacao de modelos de dados e aumento da complexidade operacional decorrente da gestao de multiplos artefatos de implantacao. Ford et al. (2022) acrescentam que a decomposicao inadequada pode gerar microsservicos excessivamente acoplados, anulando as vantagens esperadas da distribuicao. No entanto, grande parte dos estudos comparativos entre monolitos e microsservicos utiliza metricas superficiais, como contagem de linhas de codigo ou numero de arquivos, sem recorrer a indicadores mais robustos de qualidade estrutural. A Complexidade Ciclomatica [CC], proposta por McCabe (1976), quantifica o numero de caminhos independentes no grafo de controle de fluxo de um programa, permitindo avaliar a testabilidade e a propensao a defeitos. O Indice de Manutenibilidade [IM], formalizado por Coleman et al. (1994), combina volume de Halstead, CC e contagem de linhas em um unico indicador da facilidade de manutencao. Richards e Ford (2020) propoe ainda o uso de acoplamento aferente, acoplamento eferente e instabilidade como metricas de modularidade entre pacotes. A ausencia dessas metricas em estudos de migracao configura uma lacuna metodologica relevante.

Adicionalmente, o surgimento de ferramentas de Inteligencia Artificial [IA] generativa voltadas a geracao de codigo — como o Claude Code, da Anthropic — abre a possibilidade de medir a produtividade de desenvolvimento de forma objetiva. Ao utilizar um agente de IA como executor padronizado de tarefas de implementacao, variaveis humanas como experiencia previa e familiaridade com o "framework" sao controladas, e o tempo de execucao, o numero de iteracoes e o volume de codigo gerado tornam-se indicadores reprodutiveis. Essa abordagem, ainda pouco explorada na literatura, permite comparar nao apenas os artefatos resultantes de diferentes estilos arquiteturais, mas tambem o esforco necessario para produzi-los sob condicoes controladas.

O presente trabalho tem como objetivo avaliar quantitativamente o impacto da migracao de um sistema monolitico para microsservicos "serverless", utilizando DDD e "Clean Architecture", por meio de tres dimensoes: qualidade de codigo (CC, IM, acoplamento aferente e eferente, instabilidade), desempenho (latencia nos percentis p50, p90 e p95) e produtividade (tempo de implementacao assistida por IA). Para isolar o efeito da arquitetura em camadas promovida pelo DDD, um grupo de controle implementado no padrao Model-View-Controller [MVC] foi submetido aos mesmos cenarios de construcao, migracao e adicao de funcionalidade. O dominio utilizado — um sistema de catalogo e estoque com tres Contextos Delimitados — foi escolhido por ser suficientemente complexo para exercitar comunicacao assincrona entre servicos, projecoes de dados e regras de negocio em Agregados, ao mesmo tempo em que permanece tratavel dentro do escopo de um trabalho academico.

---

## Material e Metodos

Adotou-se uma abordagem de estudo de caso experimental com quatro implementacoes do mesmo sistema de gerenciamento de produtos e estoque: um monolito com "Domain-Driven Design" [DDD] (Evans, 2003), um monolito com arquitetura "Model-View-Controller" [MVC] tradicional (grupo de controle), e as respectivas migracoes de ambos para microsservicos "serverless". As quatro bases de codigo compartilharam a mesma especificacao de dominio e os mesmos contratos de "Application Programming Interface" [API], diferindo apenas na organizacao interna e nas camadas de infraestrutura. As metricas foram coletadas de forma sistematica ao longo do processo de desenvolvimento e em testes controlados apos a implantacao.

**Dominio e modelagem**

O sistema foi modelado seguindo os principios de DDD propostos por Evans (2003), com tres "Bounded Contexts" [BC] claramente delimitados: Autenticacao, Catalogo de Produtos e Controle de Estoque. A Linguagem Ubiqua foi formalizada em um glossario com onze termos fundamentais: Usuario, "Token", Produto, "Stock Keeping Unit" [SKU], Categoria, Item de Estoque, Movimentacao, Entrada, Saida, Saldo e Lote.

O contexto de Catalogo possui como raiz de agregacao a entidade Produto, composta por "Value Objects" imutaveis (SKU e Dinheiro) e referencia a entidade Categoria. O contexto de Estoque possui como raiz de agregacao o Item de Estoque, que mantem um saldo calculado a partir de entidades de Movimentacao (Entrada ou Saida). O Estoque nao conhece o dominio de Catalogo diretamente — mantem apenas uma projecao local com dados minimos (SKU, nome, categoria) recebidos por meio de eventos assincronos. Essa estrategia de projecao local, descrita por Vernon (2013) como mecanismo de integracao entre contextos, garantiu que cada BC pudesse operar de forma autonoma.

A comunicacao entre contextos foi implementada exclusivamente via eventos de dominio publicados em topico "Simple Notification Service" [SNS] e consumidos por fila "Simple Queue Service" [SQS], garantindo desacoplamento total e consistencia eventual. Os eventos definidos foram: ProdutoCriado, ProdutoAtualizado e ProdutoDesativado (emitidos pelo Catalogo) e EstoqueMovimentado e EstoqueInsuficiente (emitidos pelo Estoque).

**Arquitetura e decisoes tecnicas**

A versao DDD seguiu a "Clean Architecture" proposta por Martin (2017) com organizacao por dominio: o codigo foi estruturado em modulos correspondentes aos "Bounded Contexts", e nao em camadas horizontais. Cada modulo (auth, catalogo, estoque) continha suas proprias quatro camadas internas: dominio (agregados, entidades, "value objects", interfaces de repositorio), aplicacao (casos de uso), infraestrutura (implementacoes de repositorio) e apresentacao (controladores HTTP ou "handlers" Lambda). Um modulo compartilhado ("shared") forneceu as abstracoes base (entidade, excecao, repositorio) e configuracao de infraestrutura.

A versao monolitica DDD utilizou o "framework" FastAPI com rotas HTTP que delegavam aos casos de uso, repositorios implementados com SQLAlchemy sobre PostgreSQL e execucao em servidor "Asynchronous Server Gateway Interface" [ASGI] convencional. O "container" Docker foi limitado a 512 MB de memoria, equivalente a configuracao das funcoes Lambda.

A versao em microsservicos DDD utilizou "handlers" AWS Lambda puros, sem adaptador Mangum. Cada funcao Lambda recebia o evento do API Gateway e delegava ao mesmo caso de uso da versao monolitica. Os repositorios foram implementados com a biblioteca boto3 sobre DynamoDB. Essa decisao arquitetural — Lambda puro em vez de adaptador — foi intencional para demonstrar que a camada de aplicacao (casos de uso) era genuinamente agnostica ao mecanismo de transporte, conforme preconizado por Martin (2017).

A troca de PostgreSQL (monolito) para DynamoDB (microsservicos) demonstrou na pratica o "Repository Pattern" descrito por Percival e Gregory (2020): a interface de repositorio definida no dominio permaneceu identica e apenas a implementacao de infraestrutura mudou. Essa decisao tambem eliminou a necessidade de "NAT Gateway" na AWS, reduzindo custos operacionais.

A injecao de dependencia [DI] foi implementada com a biblioteca "dependency-injector", utilizando o padrao de "Composition Root" [CR] (Percival e Gregory, 2020): cada "Bounded Context" possuia um "container" declarativo que era o unico ponto do sistema a conhecer as implementacoes concretas dos repositorios. Os casos de uso recebiam interfaces via construtor e desconheciam se estavam conectados a PostgreSQL, DynamoDB ou repositorios em memoria (usados em testes). Essa abordagem foi preferida ao mecanismo Depends() do FastAPI por nao acoplar a composicao de dependencias ao "framework", mantendo as camadas de dominio e aplicacao como Python puro.

<!-- TODO: Adicionar diagrama da arquitetura como Figura ao passar para Word.
     Figura 1. Arquitetura do sistema monolitico DDD
     Figura 2. Arquitetura dos microsservicos "serverless" DDD
     Figura 3. Fluxo de eventos entre "Bounded Contexts"
     Fonte: Dados originais da pesquisa -->

**Grupo de controle MVC**

Para isolar o efeito da adocao de DDD sobre as metricas de qualidade e produtividade, implementou-se um grupo de controle com arquitetura MVC tradicional. O monolito MVC expunha exatamente a mesma API e os mesmos comportamentos do monolito DDD, porem com uma estrutura propositalmente simplificada: rotas com "queries" SQL diretas via SQLAlchemy, validacao "inline", sem separacao em camadas de dominio, aplicacao ou infraestrutura, sem interfaces abstratas e sem "container" de injecao de dependencia. Todo o codigo concentrou-se em poucos arquivos (app.py, models.py, schemas.py e quatro modulos de rotas).

A migracao do monolito MVC para microsservicos "serverless" seguiu o mesmo procedimento do DDD: cada modulo de rota foi convertido em um servico Lambda independente com "handlers" puros e repositorios DynamoDB. Diferentemente do DDD, nao houve reuso de camadas intermediarias — cada "handler" continha a logica de negocio, a validacao e o acesso ao banco de forma monolitica.

Essa abordagem de grupo de controle permitiu comparacoes pareadas em todas as dimensoes de interesse: complexidade ciclomatica [CC], indice de manutenibilidade [IM], acoplamento entre pacotes, tempo de construcao, tempo de migracao e tempo de implementacao de "feature" nova.

**Ferramentas e tecnologias**

As principais tecnologias utilizadas no experimento foram:

- Linguagem: Python 3.13
- "Framework" HTTP (monolito): FastAPI
- Computacao "serverless": AWS Lambda com API Gateway
- Banco de dados: PostgreSQL 16 (monolito) e DynamoDB (microsservicos)
- Mensageria: Amazon SNS e SQS
- Infraestrutura como codigo: AWS "Serverless Application Model" [SAM]
- Integracao continua: GitHub Actions
- Analise estatica: radon 6.0.1 (CC, IM, metricas de Halstead), xenon 0.9.3 ("gate" de qualidade)
- Acoplamento: grimp 3.14 (grafo de "imports", acoplamento aferente [Ca] e eferente [Ce])
- Coesao: cohesion 1.2.0 ("Lack of Cohesion of Methods" [LCOM] invertido)
- Testes de carga: k6 v0.55.0
- Simulacao de servicos AWS em testes: moto (emulacao local de DynamoDB, SNS e SQS)

**Metricas coletadas**

Para avaliar a migracao de forma quantitativa, definiram-se metricas em tres dimensoes:

*Qualidade de codigo.* A CC (McCabe, 1976) foi medida com a ferramenta radon, que atribui graus de A (baixa complexidade, 1 a 5) a F (complexidade muito alta, acima de 40) a cada funcao ou metodo. O IM foi calculado conforme a formula de Coleman et al. (1994), que combina volume de Halstead (1977), CC e linhas de codigo em escala de 0 a 100. Valores acima de 85 indicam alta manutenibilidade. O acoplamento aferente (Ca) e eferente (Ce) entre pacotes foi obtido com grimp, que constroi o grafo de "imports" Python e agrupa modulos em pacotes de dois niveis. A instabilidade foi calculada como I = Ce / (Ca + Ce), conforme proposto por Martin (1994). A coesao de classes foi medida com a ferramenta cohesion, que reporta o percentual de atributos acessados pelos metodos de cada classe (inverso do LCOM de Chidamber e Kemerer, 1994). O "gate" de qualidade xenon foi configurado com "thresholds" maximo absoluto C, maximo por modulo B e media A, funcionando como "fitness function" arquitetural (Richards e Ford, 2020).

*Desempenho.* A latencia nos percentis p50, p90 e p95 foi medida com a ferramenta k6 em cenario de carga controlada, conforme detalhado no subtopico de teste de carga.

*Produtividade com Inteligencia Artificial [IA].* Cada funcionalidade foi implementada pelo agente de IA Claude Code. Para cada implementacao registrou-se: tempo total de parede ("wall clock") do inicio do "prompt" ate codigo funcional com todos os testes aprovados, numero de iteracoes de correcao e variacao na CC e no IM antes e depois da "feature". A cronometragem foi realizada por "script" proprio que gravava marcacoes de tempo ("timestamps") no inicio e no fim de cada tarefa.

<!-- TODO: Inserir Tabela ao passar para Word:
     Tabela 1. Metricas coletadas, ferramentas e dimensoes de avaliacao
     Colunas: Dimensao | Metrica | Ferramenta | Unidade
     Fonte: Dados originais da pesquisa -->

**Procedimento experimental**

O desenvolvimento seguiu uma estrategia de "Walking Skeleton" (Newman, 2019): toda a infraestrutura (integracao continua, bancos de dados, filas de mensageria e "templates" de implantacao) foi provisionada e validada antes de qualquer implementacao de logica de negocio, contendo apenas um "endpoint" de verificacao de saude (/health). Essa abordagem isolou o tempo de configuracao de infraestrutura do tempo de desenvolvimento de funcionalidades, permitindo medicao precisa da produtividade.

Na fase de construcao do monolito DDD, as funcionalidades foram adicionadas incrementalmente na seguinte ordem: (1) autenticacao com "JSON Web Token" [JWT], (2) "Create, Read, Update, Delete" [CRUD] de Categoria, (3) CRUD de Produto com "Value Objects" SKU e Dinheiro, (4) entrada de estoque com criacao do segundo BC e (5) saida de estoque. Cada funcionalidade foi implementada em sessao unica do agente Claude Code, com cronometragem independente. O tempo total de construcao do monolito DDD foi de 24 minutos e 50 segundos, resultando em 36 testes aprovados e 1821 linhas de codigo executavel [SLOC].

O monolito MVC foi construido com a mesma ferramenta de IA e a mesma especificacao de API, porem sem instrucoes de DDD ou separacao de camadas. O tempo total foi de aproximadamente 8 minutos, resultando em 33 testes e 466 SLOC.

Na fase de migracao para microsservicos, seis agentes Claude Code foram executados em paralelo — tres para os servicos DDD (auth, catalogo, estoque) e tres para os servicos MVC equivalentes. Cada agente recebeu a tarefa de migrar um modulo do monolito para um servico Lambda independente, criando "handlers" puros, repositorios DynamoDB e configuracao SAM. Os tempos foram cronometrados individualmente por servico. O tempo somado da migracao DDD foi de 12 minutos e 36 segundos; o da migracao MVC, 6 minutos e 46 segundos. Todos os 104 testes (52 DDD e 52 MVC) foram aprovados na primeira iteracao de cada agente. Os tres servicos DDD foram implantados na AWS e validados com teste fim-a-fim em producao; os servicos MVC foram validados apenas localmente.

Por fim, na fase de "feature" nova, uma funcionalidade de alerta de estoque baixo foi especificada e implementada em quatro variantes (monolito DDD, monolito MVC, microsservico DDD e microsservico MVC) por quatro agentes em paralelo, cada um partindo de testes pre-escritos. Essa fase permitiu medir o impacto da arquitetura sobre a velocidade de adicao de funcionalidades em bases de codigo ja existentes.

**Contrato de integracao e testes-guardiao**

Para garantir que o codigo gerado pelos agentes de IA funcionasse em ambiente real e nao apenas em testes locais, elaborou-se um documento de contrato de integracao com seis regras obrigatorias para todos os microsservicos. Esse contrato foi motivado por uma classe recorrente de defeitos em que o codigo aprovava testes unitarios, porem falhava na implantacao por desalinhamento entre variaveis de ambiente do "template" SAM e as lidas pelo codigo, ou por uso de repositorios em memoria como substitutos silenciosos do DynamoDB.

As regras determinaram que: (1) cada "handler" deveria ler exatamente as variaveis de ambiente declaradas no template.yaml, sem variantes inventadas; (2) os testes deveriam utilizar a biblioteca moto para emular DynamoDB, SNS e SQS localmente, em vez de repositorios em memoria com desvio condicional; (3) todo teste de escrita deveria verificar a persistencia real via boto3; (4) consumidores de eventos deveriam gravar estado no DynamoDB, nao apenas registrar mensagens em "log"; (5) nenhuma chamada AWS deveria ocorrer em tempo de importacao do modulo; e (6) "handlers" nao deveriam capturar excecoes genericas.

Para cada servico, criou-se um arquivo de testes-guardiao (test_integration_contract.py) que parseava o template.yaml automaticamente e falhava caso qualquer variavel de ambiente declarada nao aparecesse no codigo-fonte, caso houvesse desvio condicional para repositorio em memoria ou caso consumidores de eventos nao realizassem persistencia. Esses quatro testes-guardiao foram executados junto com os testes de comportamento em todas as bases de codigo. A "fixture" de teste conftest.py, compartilhada por todos os servicos, abria o contexto mock_aws() da moto em modo "autouse", criava as tabelas, topicos e filas a partir do template.yaml e configurava as variaveis de ambiente com os nomes reais.

**Teste de carga**

A latencia em producao foi medida com a ferramenta k6 v0.55.0 em cenario de rampa: 1 a 5 usuarios virtuais [VU] durante 15 segundos de aquecimento, 10 VUs sustentados por 60 segundos e reducao gradual em 10 segundos. O fluxo funcional completo foi executado em sequencia por cada VU: registrar usuario, efetuar "login", criar categoria, criar produto, consultar estoque, registrar entrada e registrar saida. Esse cenario reproduziu a jornada completa de um operador do sistema.

O monolito DDD foi testado em instancia EC2 t3.micro com uma unica instancia, "Application Load Balancer" [ALB] e banco RDS PostgreSQL. Os microsservicos DDD foram testados com funcoes Lambda configuradas com 512 MB de memoria, API Gateway e DynamoDB no modo de cobranca por requisicao. Ambos os testes foram executados a partir da mesma maquina local, de modo que a latencia de rede estivesse incluida de forma equivalente em ambas as medicoes.

---

## Resultados e Discussao

<!-- ================================================================
     REGRAS DESTA SEÇÃO:
     - Pode ter subtópicos (negrito, recuo 1,25cm)
     - Apresentar resultados E interpretar/discutir
     - Figuras: título abaixo, "Fonte: Resultados originais da pesquisa"
     - Tabelas: título acima, "Fonte: Resultados originais da pesquisa"
     ================================================================ -->

**Qualidade de codigo e manutenibilidade**

A Tabela 2 apresenta os resultados de Complexidade Ciclomatica [CC] e Indice de Manutenibilidade [IM] obtidos para as oito bases de codigo analisadas. Todas as metricas foram extraidas com a ferramenta radon, conforme descrito na secao anterior.

<!-- Tabela 2. Complexidade ciclomatica e indice de manutenibilidade por base de codigo -->
<!-- Fonte: Resultados originais da pesquisa -->

| Base de codigo | Arquitetura | SLOC | Blocos | CC medio | IM medio |
|----------------|-------------|------|--------|----------|----------|
| Monolito DDD | DDD | 1821 | 228 | 1,84 | 90,28 |
| Monolito MVC | MVC | 466 | 43 | 1,86 | 75,04 |
| Microsservico Auth | DDD | 344 | 62 | 1,73 | 93,25 |
| Microsservico Catalogo | DDD | 676 | 94 | 2,31 | 81,89 |
| Microsservico Estoque | DDD | 685 | 83 | 2,22 | 87,28 |
| Microsservico Auth | MVC | 103 | 10 | 2,50 | 88,66 |
| Microsservico Catalogo | MVC | 240 | 20 | 3,90 | 83,13 |
| Microsservico Estoque | MVC | 257 | 22 | 2,82 | 80,54 |

Todas as bases de codigo apresentaram CC medio na faixa A (1 a 5) da escala proposta por McCabe (1976), o que indica baixa complexidade por funcao ou metodo individual. Contudo, a comparacao entre arquiteturas revela diferencas consistentes. A media global de CC das quatro bases DDD foi de 2,03, enquanto a das quatro bases MVC foi de 2,77 — uma diferenca de 27%. Esse resultado sugere que a decomposicao em camadas e a separacao de responsabilidades promovidas pelo DDD produziram funcoes menores e com menos caminhos de decisao.

A diferenca e mais acentuada nos microsservicos de Catalogo, onde o DDD obteve CC de 2,31 contra 3,90 do MVC. No MVC, a logica de validacao, acesso a dados e formatacao de resposta concentrou-se em poucos "handlers", elevando o numero de ramificacoes por funcao. No DDD, a mesma logica foi distribuida entre entidades de dominio, casos de uso e repositorios, cada um com responsabilidade delimitada.

O IM apresentou diferenca ainda mais expressiva. No monolito, o DDD atingiu 90,28 — classificado como alta manutenibilidade segundo a escala de Coleman et al. (1994) — enquanto o MVC obteve 75,04, na faixa moderada. Essa diferenca de 15,24 pontos representa o maior delta observado entre todas as comparacoes pareadas. Nos microsservicos, a diferenca se reduziu: o IM medio DDD foi de 87,47 contra 84,11 do MVC, uma diferenca de 3,36 pontos. A convergencia nos microsservicos pode ser explicada pelo menor tamanho de cada servico: com menos linhas de codigo, mesmo o MVC produz arquivos curtos e de baixa complexidade, o que eleva o IM.

O "gate" de qualidade xenon, configurado com "thresholds" maximo absoluto C, maximo por modulo B e media A, foi aprovado por sete das oito bases de codigo. A unica falha ocorreu no microsservico Catalogo DDD, que possui um "handler" de roteamento com CC superior ao limite B. Essa funcao concentra o despacho de rotas HTTP para os casos de uso correspondentes e representa um ponto de melhoria identificado pela "fitness function" arquitetural, conforme conceituado por Richards e Ford (2020).

**Acoplamento e coesao**

A analise de acoplamento entre pacotes foi realizada com a ferramenta grimp, que constroi o grafo de "imports" Python e calcula o acoplamento aferente (Ca), eferente (Ce) e a instabilidade (I = Ce / (Ca + Ce)) por pacote, conforme proposto por Martin (1994). A Tabela 3 apresenta os resultados agregados por base de codigo.

<!-- Tabela 3. Acoplamento entre pacotes e coesao de classes por base de codigo -->
<!-- Fonte: Resultados originais da pesquisa -->

| Base de codigo | Arquitetura | Pacotes | Modulos | Instabilidade media | Classes | Coesao media (%) |
|----------------|-------------|---------|---------|---------------------|---------|------------------|
| Monolito DDD | DDD | 6 | 117 | 0,417 | 87 | 32,29 |
| Monolito MVC | MVC | 4 | 5 | 0,000 | 0 | 0,00 |
| Microsservico Auth | DDD | 6 | 34 | 0,458 | 18 | 28,24 |
| Microsservico Catalogo | DDD | 5 | 21 | 0,450 | 28 | 48,87 |
| Microsservico Estoque | DDD | 5 | 35 | 0,450 | 21 | 39,15 |
| Microsservico Auth | MVC | 1 | 5 | 0,000 | 0 | 0,00 |
| Microsservico Catalogo | MVC | 1 | 4 | 0,000 | 0 | 0,00 |
| Microsservico Estoque | MVC | 1 | 5 | 0,000 | 0 | 0,00 |

As bases DDD apresentaram instabilidade media entre 0,417 e 0,458, valores na faixa de equilibrio (0,3 a 0,7) da escala de Martin (1994). Esse resultado reflete a organizacao em camadas direcionais: os pacotes de apresentacao ("handlers") dependem dos pacotes de aplicacao, que dependem do dominio, que por sua vez depende apenas do modulo compartilhado. No monolito DDD, por exemplo, o pacote "src.presentation" possui Ce = 4 e Ca = 0 (instabilidade 1,0), pois depende de todos os "Bounded Contexts" sem ser dependencia de nenhum. O pacote "src.shared", ao contrario, possui Ca = 4 e Ce = 0 (instabilidade 0,0), configurando-se como o componente mais estavel do sistema — exatamente o papel esperado para abstracoes base, conforme a regra de inversao de dependencia de Martin (2017).

As bases MVC registraram instabilidade 0,000 em todos os pacotes. Esse valor nao indica estabilidade superior, mas reflete a impossibilidade de medicao: cada servico MVC possui apenas um pacote (src.handlers) sem dependencias internas entre modulos. A ausencia de pacotes com acoplamento aferente e eferente torna a metrica trivial, nao informativa. Richards e Ford (2020) observam que a modularidade so pode ser avaliada quando ha fronteiras explicitas entre componentes. No MVC, a ausencia dessas fronteiras impede a aplicacao de metricas de acoplamento, o que constitui uma limitacao estrutural e nao uma vantagem arquitetural.

A coesao de classes, medida pela ferramenta cohesion como o percentual medio de atributos acessados pelos metodos de cada classe (inverso do LCOM de Chidamber e Kemerer, 1994), foi mensuravel apenas nas bases DDD. Os valores variaram de 28,24% (microsservico Auth) a 48,87% (microsservico Catalogo). Essa variacao reflete a natureza dos agregados em cada contexto: o Catalogo possui entidades com atributos coesos (Produto referencia SKU, Dinheiro e Categoria no mesmo fluxo), enquanto o Auth possui classes de servico com metodos mais independentes (registrar, autenticar, validar "token").

As bases MVC nao possuem classes — toda a logica e implementada em funcoes puras nos "handlers" — o que impossibilitou a medicao de coesao. Essa e uma consequencia direta da escolha arquitetural: o MVC privilegia funcoes procedurais, enquanto o DDD organiza o comportamento em torno de objetos de dominio com estado e invariantes.

**Desempenho e latencia**

Os resultados do teste de carga com k6 sao apresentados na Tabela 4, que compara a latencia por "endpoint" entre o monolito DDD (EC2 t3.micro com ALB) e os microsservicos DDD (Lambda 512 MB com API Gateway).

<!-- Tabela 4. Latencia por "endpoint" — monolito DDD vs microsservicos DDD -->
<!-- Fonte: Resultados originais da pesquisa -->

| Endpoint | Alvo | p50 (ms) | p90 (ms) | p95 (ms) | Media (ms) |
|----------|------|----------|----------|----------|------------|
| health | Monolito | 137 | 250 | 253 | 174 |
| health | Microsservico | 373 | 486 | 501 | 316 |
| registrar | Monolito | 887 | 1323 | 1445 | 913 |
| registrar | Microsservico | 1530 | 1648 | 1734 | 1532 |
| login | Monolito | 917 | 1311 | 1416 | 896 |
| login | Microsservico | 1460 | 1517 | 1613 | 1479 |
| criar categoria | Monolito | 147 | 250 | 253 | 177 |
| criar categoria | Microsservico | 497 | 562 | 651 | 530 |
| criar produto | Monolito | 194 | 252 | 255 | 207 |
| criar produto | Microsservico | 635 | 739 | 752 | 588 |
| buscar estoque | Microsservico | 264 | 505 | 530 | 369 |
| entrada estoque | Microsservico | 426 | 694 | 723 | 489 |
| saida estoque | Microsservico | 445 | 684 | 746 | 506 |

O monolito apresentou latencia de duas a tres vezes menor que os microsservicos no percentil 50 para todos os "endpoints" comparaveis. No "endpoint" health, o monolito registrou p50 de 137 ms contra 373 ms dos microsservicos. Nos "endpoints" de CRUD simples (criar categoria e criar produto), o monolito obteve p50 entre 147 e 194 ms, enquanto os microsservicos variaram entre 497 e 635 ms. Essa diferenca e explicada pelo "overhead" fixo da cadeia API Gateway e Lambda: cada requisicao precisa atravessar o roteamento do API Gateway, inicializar o contexto da funcao Lambda (quando ocorre inicializacao a frio ou "cold start") e retornar pela mesma cadeia.

Os "endpoints" de autenticacao (registrar e "login") foram os mais lentos em ambas as arquiteturas, com p50 entre 887 e 917 ms no monolito e entre 1460 e 1530 ms nos microsservicos. Essa latencia elevada e dominada pelo custo computacional do algoritmo bcrypt, utilizado para derivacao de senha. O bcrypt e intencionalmente lento — por projeto criptografico — e consome ciclos de "CPU" proporcionais ao fator de custo configurado. A diferenca absoluta entre monolito e microsservico (~570 ms) permanece na mesma ordem de grandeza do "overhead" observado nos demais "endpoints", sugerindo que o bcrypt adiciona um custo base constante sobre o qual o "overhead" de infraestrutura se soma.

Um resultado relevante foi o comportamento nos percentis superiores. Enquanto o monolito apresentou dispersao significativa entre p50 e p95 — por exemplo, de 887 ms para 1445 ms no "endpoint" registrar, um aumento de 63% — os microsservicos exibiram dispersao menor: de 1530 ms para 1734 ms, aumento de apenas 13%. Esse padrao indica que os microsservicos, apoiados pela escalabilidade horizontal automatica do Lambda, oferecem latencia mais previsivel sob carga, mesmo que a latencia absoluta seja maior. O monolito em instancia t3.micro, com recursos fixos de CPU e memoria, sofre degradacao mais acentuada quando multiplos usuarios concorrentes executam operacoes computacionalmente intensivas como o bcrypt.

**Produtividade assistida por inteligencia artificial**

Os tempos de implementacao por agente de IA foram registrados em tres fases: construcao do monolito (Fase A), migracao para microsservicos (Fase B) e implementacao de "feature" nova (Fase C). A Tabela 5 consolida os resultados de todas as fases. Antes da leitura da tabela, cabe esclarecer a interpretacao das colunas: o tempo na Fase B apresenta-se em duas linhas, "somado" e "paralelo (max)"; a linha "somado" corresponde a soma dos tempos individuais dos tres microsservicos, representando o esforco equivalente caso a migracao fosse sequencial, enquanto "paralelo (max)" corresponde ao tempo real de parede ("wall clock") observado, uma vez que os tres agentes foram disparados simultaneamente e o tempo total equivale ao do servico mais lento. A coluna Testes, nas fases A e B, apresenta o numero absoluto de testes aprovados; na Fase C, adota-se a notacao "novos/total", em que o numerador e o numero de testes novos adicionados pela feature (quatro em todas as variantes) e o denominador e o numero total de testes aprovados apos a implementacao, incluindo os testes preexistentes — ambos passando, o que evidencia ausencia de regressao.

<!-- Tabela 5. Tempos de implementacao por fase e arquitetura -->
<!-- Fonte: Resultados originais da pesquisa -->

| Fase | Variante | Tempo | Testes | Iteracoes | SLOC |
|------|----------|-------|--------|-----------|------|
| A — Construcao monolito | DDD | 24min 50s | 36 | 1 por "feature" | 1821 |
| A — Construcao monolito | MVC | ~8min | 33 | 1 | 466 |
| B — Migracao (somado) | DDD | 12min 36s | 52/52 | 1 por servico | — |
| B — Migracao (somado) | MVC | 6min 46s | 52/52 | 1 por servico | — |
| B — Migracao (paralelo max) | DDD | 4min 33s | — | — | — |
| B — Migracao (paralelo max) | MVC | 2min 31s | — | — | — |
| C — Feature (monolito) | DDD | 3min 31s | 4/40 | 1 | — |
| C — Feature (monolito) | MVC | 1min 53s | 4/37 | 1 | — |
| C — Feature (microsservico) | DDD | 3min 01s | 4/24 | 1 | — |
| C — Feature (microsservico) | MVC | 1min 35s | 4/24 | 1 | — |

O padrao mais consistente observado foi a vantagem de velocidade do MVC sobre o DDD em todas as fases. Na construcao do monolito, o DDD demandou 24 minutos e 50 segundos contra aproximadamente 8 minutos do MVC — o MVC foi cerca de tres vezes mais rapido. Na migracao, o tempo somado do MVC (6 minutos e 46 segundos) foi 46% menor que o do DDD (12 minutos e 36 segundos). Na "feature" nova, o MVC foi 47% mais rapido no monolito (1 minuto e 53 segundos contra 3 minutos e 31 segundos) e tambem 47% mais rapido no microsservico (1 minuto e 35 segundos contra 3 minutos e 1 segundo).

Essa diferenca de velocidade esta diretamente relacionada ao volume de codigo e ao numero de artefatos que cada arquitetura exige. A implementacao DDD requer a criacao de entidades de dominio, "value objects", interfaces de repositorio, implementacoes concretas, casos de uso e "schemas" de entrada e saida, distribuidos em multiplos arquivos e camadas. Na "feature" de alerta de estoque baixo, por exemplo, o DDD criou cinco arquivos novos e modificou sete no monolito, enquanto o MVC nao criou nenhum arquivo novo e modificou apenas tres.

Um aspecto relevante e que todas as doze implementacoes (cinco "features" do monolito DDD, construcao do monolito MVC, seis migracoes e quatro "features" novas) convergiram na primeira iteracao do agente de IA, sem necessidade de re-"prompt" ou correcao manual. Todos os 104 testes da migracao (52 DDD e 52 MVC) e os 16 testes da fase de "feature" nova foram aprovados integralmente. Todos os seis servicos implantados na AWS (tres DDD em producao, tres MVC validados localmente) funcionaram corretamente na primeira tentativa de implantacao. Esse resultado indica que a especificacao formal do dominio e os contratos de integracao fornecidos como contexto ao agente de IA foram suficientes para guiar a geracao de codigo funcional independentemente da complexidade arquitetural.

Na migracao, observou-se que o DDD permite reutilizacao significativa das camadas de dominio e aplicacao. Os casos de uso, entidades e "value objects" permaneceram identicos entre monolito e microsservicos — apenas a camada de infraestrutura (repositorios e "handlers") foi substituida. Essa propriedade, derivada da regra de dependencia da "Clean Architecture" (Martin, 2017), significa que a migracao DDD exige reescrever somente a periferia do sistema. No MVC, por outro lado, cada "handler" concentra toda a logica, de modo que a migracao equivale a reescrever o servico inteiro.

**Comparacao DDD vs MVC — sintese**

A Tabela 6 consolida as principais metricas das duas arquiteturas, permitindo uma visao comparativa cruzada das dimensoes analisadas.

<!-- Tabela 6. Comparacao cruzada DDD vs MVC nas principais dimensoes -->
<!-- Fonte: Resultados originais da pesquisa -->

| Dimensao | Metrica | DDD | MVC | Observacao |
|----------|---------|-----|-----|------------|
| Tamanho | SLOC (monolito) | 1821 | 466 | DDD ~3,9x maior |
| Complexidade | CC medio (global) | 2,03 | 2,77 | DDD 27% menor |
| Manutenibilidade | IM medio (global) | 88,18 | 81,84 | DDD 6,3 pontos maior |
| Manutenibilidade | IM (monolito) | 90,28 | 75,04 | DDD 15,2 pontos maior |
| Acoplamento | Instabilidade media | 0,44 | 0,00 | MVC nao mensuravel |
| Coesao | Coesao media (%) | 28-49 | 0 | MVC sem classes |
| Latencia | p50 CRUD (ms) | 147-194 | — | Monolito DDD |
| Latencia | p50 CRUD (ms) | 497-635 | — | Microsservico DDD |
| Produtividade | Construcao monolito | 24min 50s | ~8min | MVC ~3x mais rapido |
| Produtividade | Migracao somada | 12min 36s | 6min 46s | MVC 46% mais rapido |
| Produtividade | Feature monolito | 3min 31s | 1min 53s | MVC 47% mais rapido |
| Qualidade | Xenon (gate) | 3/4 PASS | 4/4 PASS | DDD 1 falha (Catalogo) |

Os resultados revelam um "trade-off" claro entre as duas abordagens. O DDD produziu codigo com menor complexidade ciclomatica e maior manutenibilidade, especialmente no monolito, onde a diferenca de IM atingiu 15 pontos. Alem disso, somente o DDD permitiu a medicao de acoplamento entre pacotes e coesao de classes, o que torna as propriedades arquiteturais visiveis e monitoraveis por ferramentas automatizadas. Essa visibilidade e essencial para a pratica de "fitness functions" arquiteturais, conforme defendido por Richards e Ford (2020), que propoe a validacao continua de propriedades estruturais como parte do ciclo de desenvolvimento.

Em contrapartida, o MVC foi consistentemente mais rapido em todas as fases de desenvolvimento e produziu significativamente menos codigo. A diferenca de velocidade (46 a 53% na migracao e "feature" nova) pode ser decisiva em cenarios onde o tempo de entrega e a restricao predominante e o dominio de negocio e suficientemente simples para dispensar separacao explicita de camadas.

E relevante observar que a complexidade ciclomatica do MVC, embora maior, permaneceu na faixa A em quase todas as bases de codigo, com excecao do microsservico Catalogo MVC (CC = 3,90, ainda na faixa A). A diferenca entre as arquiteturas, portanto, nao se manifesta como defeito de qualidade no MVC, mas como ausencia de estrutura para evolucao: a medida que o dominio cresce, a concentracao de logica em poucos arquivos tende a elevar a CC de forma mais acentuada do que a distribuicao em camadas do DDD.

**Limitacoes**

Os resultados devem ser interpretados considerando as seguintes limitacoes do estudo. Primeiro, o dominio modelado e relativamente simples, com tres "Bounded Contexts", 1821 SLOC no monolito DDD e apenas onze termos na Linguagem Ubiqua. Dominios empresariais reais tendem a ser significativamente mais complexos, e os beneficios do DDD podem ser mais pronunciados — ou os custos mais elevados — em escala maior.

Segundo, o teste de carga foi conduzido com no maximo 10 usuarios virtuais e duracao de 60 segundos em regime sustentado. Esse cenario e insuficiente para extrapolar conclusoes sobre comportamento em producao com centenas ou milhares de usuarios concorrentes. Aspectos como inicializacao a frio ("cold start") em escala, exaustao de conexoes e limites de concorrencia do Lambda nao foram exercitados.

Terceiro, os resultados de produtividade sao inerentemente dependentes do agente de IA utilizado (Claude Code), da versao do modelo, do contexto fornecido e da formulacao do "prompt". Embora todas as implementacoes tenham sido realizadas com o mesmo modelo e formato de instrucoes, nao ha garantia de que uma repeticao do experimento produziria tempos identicos. A variabilidade estocastica dos modelos de linguagem e uma limitacao metodologica conhecida.

Quarto, o mesmo desenvolvedor elaborou as especificacoes, os "prompts" e os contratos de integracao para ambas as arquiteturas, o que pode introduzir vies favoravel ao DDD — a arquitetura escolhida como foco do estudo. A mitigacao desse risco foi feita pela utilizacao do mesmo agente de IA para todas as implementacoes e pela padronizacao dos contratos de API.

Por fim, as metricas de analise estatica capturam aspectos estruturais do codigo, mas nao abrangem todas as dimensoes de qualidade de "software". Propriedades como legibilidade, adequacao ao dominio, facilidade de "debugging" e custo de integracao de novos desenvolvedores nao foram avaliadas neste estudo.

---

## Conclusao

A migracao de um monolito para microsservicos "serverless" utilizando DDD e "Clean Architecture" mostrou-se viavel e produziu melhorias mensuraveis na qualidade estrutural do codigo. O objetivo principal do trabalho — avaliar quantitativamente o impacto dessa migracao por meio de metricas de qualidade, desempenho e produtividade assistida por IA — foi atendido nas tres dimensoes propostas.

O DDD produziu codigo com CC 27% menor e IM 6,3 pontos superior ao MVC na media global das oito bases de codigo. No monolito, onde a diferenca de IM atingiu 15,2 pontos (90,28 contra 75,04), a vantagem foi mais expressiva. Alem disso, somente o DDD permitiu a medicao de acoplamento entre pacotes e coesao de classes, tornando as propriedades arquiteturais visiveis para monitoramento automatizado. O MVC, por nao possuir fronteiras explicitas entre componentes, inviabilizou a aplicacao dessas metricas.

O "Repository Pattern" demonstrou na pratica sua funcao de desacoplamento entre dominio e infraestrutura. A troca de PostgreSQL para DynamoDB durante a migracao exigiu apenas a substituicao das implementacoes concretas de repositorio, sem alteracao nas camadas de dominio e aplicacao. Essa propriedade, derivada da regra de dependencia da "Clean Architecture", reduziu o escopo da migracao DDD as camadas perifericas do sistema.

A comunicacao assincrona via SNS e SQS entre "Bounded Contexts" garantiu desacoplamento total entre os microsservicos de Catalogo e Estoque. O mecanismo de projecao local permitiu que cada servico operasse de forma autonoma, sem dependencia sincrona de outros contextos. O fluxo completo — da criacao de produto ate a consulta de estoque com saldo atualizado — foi validado em producao com sucesso.

O "trade-off" entre DDD e MVC revelou-se consistente em todas as fases do experimento. O MVC foi entre 46% e tres vezes mais rapido na construcao e migracao, com volume de codigo significativamente menor (466 contra 1821 SLOC no monolito). Em contrapartida, o MVC concentrou logica em poucos arquivos, o que tende a elevar a CC de forma mais acentuada a medida que o dominio cresce. A escolha entre as duas abordagens depende, portanto, do horizonte de evolucao do sistema: para dominios simples e ciclos de entrega curtos, o MVC oferece vantagem em velocidade; para dominios complexos com expectativa de evolucao continua, o DDD oferece estrutura que preserva a manutenibilidade ao longo do tempo.

A produtividade com agentes de IA foi elevada em ambas as arquiteturas. Todas as doze implementacoes convergiram na primeira iteracao, com 100% dos testes aprovados e todos os servicos funcionais na primeira tentativa de implantacao. Esse resultado, porem, dependeu criticamente da qualidade dos artefatos fornecidos como contexto: especificacao formal do dominio, contratos de API e, sobretudo, o contrato de integracao com testes-guardiao. A ausencia inicial desse contrato havia produzido codigo que passava em testes locais mas falhava na implantacao; sua introducao elevou a taxa de sucesso de implantacao de 33% para 100%. Conclui-se que a eficacia da geracao de codigo por IA esta condicionada a existencia de especificacoes formais e mecanismos de verificacao automatizada que constranjam a saida do modelo.

Em termos de desempenho, os microsservicos apresentaram latencia de duas a tres vezes maior que o monolito no percentil 50, em razao do "overhead" fixo da cadeia API Gateway e Lambda. Contudo, os microsservicos exibiram dispersao menor entre p50 e p95, indicando latencia mais previsivel sob carga. Esse resultado sugere que a decisao entre monolito e microsservicos "serverless" deve considerar nao apenas a latencia absoluta, mas tambem a previsibilidade e a capacidade de escalabilidade automatica.

O estudo possui limitacoes que restringem a generalizacao dos resultados: o dominio modelado e simples (tres "Bounded Contexts", 1821 SLOC), o teste de carga foi conduzido com no maximo 10 usuarios virtuais e os resultados de produtividade sao dependentes do agente de IA, do modelo e do contexto fornecido.

Como trabalhos futuros, sugere-se: (1) a replicacao do experimento em dominios de maior complexidade, com dezenas de "Bounded Contexts" e equipes multiplas, para verificar se os beneficios do DDD se ampliam proporcionalmente; (2) a comparacao entre diferentes modelos de IA e configuracoes de "prompt" para quantificar a variabilidade estocastica na geracao de codigo; (3) a aplicacao de tecnicas de engenharia do caos para avaliar a resiliencia dos microsservicos sob condicoes de falha; e (4) a analise de custo operacional em cenarios de carga real prolongada, incluindo aspectos como inicializacao a frio em escala e limites de concorrencia do Lambda.

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

Chidamber, S.R.; Kemerer, C.F. 1994. A metrics suite for object-oriented design. IEEE Transactions on Software Engineering 20(6): 476-493.

Coleman, D.; Ash, D.; Lowther, B.; Oman, P. 1994. Using metrics to evaluate software system maintainability. Computer 27(8): 44-49.

Evans, E. 2003. Domain-Driven Design: Tackling Complexity in the Heart of Software. 1ed. Addison-Wesley, Boston, MA, USA.

Ford, N.; Richards, M.; Sadalage, P.; Dehghani, Z. 2022. Software Architecture: The Hard Parts. 1ed. O'Reilly Media, Sebastopol, CA, USA.

Halstead, M.H. 1977. Elements of Software Science. 1ed. Elsevier, New York, NY, USA.

Martin, R.C. 1994. OO Design Quality Metrics: An Analysis of Dependencies. Object Mentor, Gurnee, IL, USA.

Martin, R.C. 2017. Clean Architecture: A Craftsman's Guide to Software Structure and Design. 1ed. Prentice Hall, Upper Saddle River, NJ, USA.

McCabe, T.J. 1976. A complexity measure. IEEE Transactions on Software Engineering SE-2(4): 308-320.

Newman, S. 2019. Monolith to Microservices: Evolutionary Patterns to Transform Your Monolith. 1ed. O'Reilly Media, Sebastopol, CA, USA.

Newman, S. 2021. Building Microservices: Designing Fine-Grained Systems. 2ed. O'Reilly Media, Sebastopol, CA, USA.

Percival, H.; Gregory, B. 2020. Architecture Patterns with Python: Enabling Test-Driven Development, Domain-Driven Design, and Event-Driven Microservices. 1ed. O'Reilly Media, Sebastopol, CA, USA.

Richards, M.; Ford, N. 2020. Fundamentals of Software Architecture: An Engineering Approach. 1ed. O'Reilly Media, Sebastopol, CA, USA.

Vernon, V. 2013. Implementing Domain-Driven Design. 1ed. Addison-Wesley, Upper Saddle River, NJ, USA.

---

## Apendice

<!-- Opcional — material complementar elaborado pelo autor -->

<!-- Possíveis apêndices:
     A. Especificação completa do domínio (spec.md)
     B. Contratos de API detalhados
     C. Resultados completos dos testes de carga (k6)
     D. Logs de sessão com Claude Code e Codex (evidência das medições)
-->
