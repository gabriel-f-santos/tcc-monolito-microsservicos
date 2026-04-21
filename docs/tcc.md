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

A migração de sistemas monolíticos para microsserviços é uma tendência consolidada na engenharia de software, porém frequentemente avaliada com métricas superficiais. Este trabalho teve como objetivo avaliar quantitativamente o impacto da migração de um monolito para microsserviços serverless utilizando Domain-Driven Design e Clean Architecture, por meio de métricas de qualidade de código, desempenho e produtividade assistida por inteligência artificial. Adotou-se um estudo de caso experimental com quatro implementações do mesmo sistema de catálogo e estoque — monolito DDD, monolito MVC (grupo de controle) e suas respectivas migrações para AWS Lambda — totalizando oito bases de código. As métricas de complexidade ciclomática, índice de manutenibilidade, acoplamento entre pacotes e latência foram coletadas com ferramentas de análise estática (radon, grimp) e testes de carga (k6). O DDD produziu código com complexidade ciclomática 27% menor e índice de manutenibilidade 6,3 pontos superior ao MVC na média global, com diferença de 15,2 pontos no monolito (90,28 contra 75,04). Os microsserviços apresentaram latência duas a três vezes maior que o monolito no percentil 50, porém com dispersão menor entre p50 e p95, indicando maior previsibilidade. O MVC foi entre 46% e três vezes mais rápido em todas as fases de desenvolvimento. Todas as doze implementações por agente de IA convergiram na primeira iteração com 100% dos testes aprovados. Conclui-se que o DDD oferece vantagens estruturais mensuráveis em manutenibilidade e modularidade, enquanto o MVC oferece maior velocidade de entrega, configurando um trade-off dependente da complexidade do domínio e do horizonte de evolução do sistema.

**Palavras-chave:** microsserviços; "serverless"; "Domain-Driven Design"; análise estática; produtividade

---

<!-- Seção opcional -->
## Migration from monolith to Serverless microservices with Domain-Driven Design

## Abstract

Migrating monolithic systems to microservices is a well-established trend in software engineering, yet it is frequently assessed using superficial metrics. This study aimed to quantitatively evaluate the impact of migrating a monolith to serverless microservices using Domain-Driven Design and Clean Architecture, measuring code quality, performance, and AI-assisted productivity. An experimental case study was conducted with four implementations of the same product catalog and inventory system — a DDD monolith, an MVC monolith (control group), and their respective migrations to AWS Lambda — totaling eight codebases. Cyclomatic complexity, maintainability index, package coupling, and latency metrics were collected using static analysis tools (radon, grimp) and load testing (k6). DDD produced code with 27% lower cyclomatic complexity and a maintainability index 6.3 points higher than MVC on a global average, with a 15.2-point difference in the monolith (90.28 versus 75.04). Microservices exhibited two to three times higher latency than the monolith at the 50th percentile, yet showed lower dispersion between p50 and p95, indicating greater predictability. MVC was between 46% and three times faster across all development phases. All twelve AI agent implementations converged on the first iteration with 100% of tests passing. It is concluded that DDD provides measurable structural advantages in maintainability and modularity, while MVC offers faster delivery speed, resulting in a trade-off dependent on domain complexity and the system's expected evolution horizon.

**Keywords:** microservices; serverless; Domain-Driven Design; static analysis; productivity

---

## Introdução

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

A adocao de arquiteturas baseadas em microsserviços tem se consolidado como alternativa ao modelo monolítico tradicional em organizações que buscam escalabilidade independente, ciclos de implantação mais curtos e autonomia entre equipes. Newman (2021) descreve microsserviços como serviços independentemente implantáveis, modelados em torno de um domínio de negócio, que se comunicam por meio de interfaces bem definidas. Em paralelo, o modelo de computação "serverless", no qual o provedor de nuvem gerência a infraestrutura de execução e cobra apenas pelo tempo efetivo de processamento, tem reduzido a barreira operacional para a implantação de arquiteturas distribuídas. Richards e Ford (2020) argumentam que decisões arquiteturais devem ser orientadas por métricas objetivas — como acoplamento, coesao e modularidade — e não apenas por preferências tecnologicas, o que reforça a necessidade de avaliações quantitativas na comparação entre estilos arquiteturais.

O Domain-Driven Design [DDD], proposto por Evans (2003), oferece ferramentas conceituais para lidar com a complexidade inerente a sistemas de software, entre as quais se destacam os Contextos Delimitados [do ingles "Bounded Contexts"], os Agregados é a Linguagem Ubíqua. Essas abstraccoes permitem definir fronteiras explícitas entre subdominios de negócio, o que se traduz naturalmente em limites de serviços quando da adocao de microsserviços. Vernon (2013) detalha a aplicação prática dessas construcoes, demonstrando como Contextos Delimitados podem encapsular modelos autônomos com regras de negócio independentes. A "Clean Architecture", sistematizada por Martin (2017), complementa o DDD ao estabelecer a regra de dependência — na qual camadas externas dependem das internas, mas nunca o contrario —, promovendo o desacoplamento entre lógica de domínio e detalhes de infraestrutura. Percival e Gregory (2020) demonstram a aplicação conjunta do "Repository Pattern" e da inversao de dependência em Python, viabilizando a substituicao de tecnologias de persistência sem alteração nas camadas de domínio e aplicação.

Apesar dos beneficios teóricos, a migração de um monolito para microsserviços introduz desafios concretos. Newman (2019) cataloga riscos recorrentes nesse processo, incluindo acoplamento entre serviços, duplicação de modelos de dados e aumento da complexidade operacional decorrente da gestao de multiplos artefatos de implantação. Ford et al. (2022) acrescentam que a decomposição inadequada pode gerar microsserviços excessivamente acoplados, anulando as vantagens esperadas da distribuicao. No entanto, grande parte dos estudos comparativos entre monolitos e microsserviços utiliza métricas superficiais, como contagem de linhas de código ou número de arquivos, sem recorrer a indicadores mais robustos de qualidade estrutural. A Complexidade Ciclomática [CC], proposta por McCabe (1976), quantifica o número de caminhos independentes no grafo de controle de fluxo de um programa, permitindo avaliar a testabilidade é a propensao a defeitos. O Índice de Manutenibilidade [IM], formalizado por Coleman et al. (1994), combina volume de Halstead, CC e contagem de linhas em um único indicador da facilidade de manutenção. Richards e Ford (2020) propoe ainda o uso de acoplamento aferente, acoplamento eferente e instabilidade como métricas de modularidade entre pacotes. A ausência dessas métricas em estudos de migração configura uma lacuna metodológica relevante.

Adicionalmente, o surgimento de ferramentas de Inteligência Artificial [IA] generativa voltadas a geração de código — como o Claude Code, da Anthropic — abre a possibilidade de medir a produtividade de desenvolvimento de forma objetiva. Ao utilizar um agente de IA como executor padronizado de tarefas de implementação, variáveis humanas como experiência previa e familiaridade com o "framework" sao controladas, é o tempo de execução, o número de iterações é o volume de código gerado tornam-se indicadores reprodutiveis. Essa abordagem, ainda pouco explorada na literatura, permite comparar não apenas os artefatos resultantes de diferentes estilos arquiteturais, mas também o esforco necessário para produzi-los sob condições controladas.

O presente trabalho tem como objetivo avaliar quantitativamente o impacto da migração de um sistema monolítico para microsserviços "serverless", utilizando DDD e "Clean Architecture", por meio de três dimensoes: qualidade de código (CC, IM, acoplamento aferente e eferente, instabilidade), desempenho (latência nos percentis p50, p90 e p95) e produtividade (tempo de implementação assistida por IA). Para isolar o efeito da arquitetura em camadas promovida pelo DDD, um grupo de controle implementado no padrao Model-View-Controller [MVC] foi submetido aos mesmos cenários de construcao, migração e adicao de funcionalidade. O domínio utilizado — um sistema de catálogo e estoque com três Contextos Delimitados — foi escolhido por ser suficientemente complexo para exercitar comunicação assincrona entre serviços, projeções de dados e regras de negócio em Agregados, ao mesmo tempo em que permanece tratável dentro do escopo de um trabalho acadêmico.

---

## Material e Métodos

Adotou-se uma abordagem de estudo de caso experimental com quatro implementações do mesmo sistema de gerenciamento de produtos e estoque: um monolito com "Domain-Driven Design" [DDD] (Evans, 2003), um monolito com arquitetura "Model-View-Controller" [MVC] tradicional (grupo de controle), e as respectivas migrações de ambos para microsserviços "serverless". As quatro bases de código compartilharam a mesma especificação de domínio é os mesmos contratos de "Application Programming Interface" [API], diferindo apenas na organização interna e nas camadas de infraestrutura. As métricas foram coletadas de forma sistemática ao longo do processo de desenvolvimento e em testes controlados após a implantação.

**Domínio e modelagem**

O sistema foi modelado seguindo os principios de DDD propostos por Evans (2003), com três "Bounded Contexts" [BC] claramente delimitados: Autenticação, Catálogo de Produtos e Controle de Estoque. A Linguagem Ubíqua foi formalizada em um glossario com onze termos fundamentais: Usuario, "Token", Produto, "Stock Keeping Unit" [SKU], Categoria, Item de Estoque, Movimentação, Entrada, Saida, Saldo e Lote.

O contexto de Catálogo possui como raiz de agregação a entidade Produto, composta por "Value Objects" imutáveis (SKU e Dinheiro) e referência a entidade Categoria. O contexto de Estoque possui como raiz de agregação o Item de Estoque, que mantém um saldo calculado a partir de entidades de Movimentação (Entrada ou Saida). O Estoque não conhece o domínio de Catálogo diretamente — mantém apenas uma projeção local com dados mínimos (SKU, nome, categoria) recebidos por meio de eventos assincronos. Essa estrategia de projeção local, descrita por Vernon (2013) como mecanismo de integração entre contextos, garantiu que cada BC pudesse operar de forma autônoma.

A comunicação entre contextos foi implementada exclusivamente via eventos de domínio publicados em tópico "Simple Notification Service" [SNS] e consumidos por fila "Simple Queue Service" [SQS], garantindo desacoplamento total e consistência eventual. Os eventos definidos foram: ProdutoCriado, ProdutoAtualizado e ProdutoDesativado (emitidos pelo Catálogo) e EstoqueMovimentado e EstoqueInsuficiente (emitidos pelo Estoque).

**Arquitetura e decisões técnicas**

A versão DDD seguiu a "Clean Architecture" proposta por Martin (2017) com organização por domínio: o código foi estruturado em módulos correspondentes aos "Bounded Contexts", e não em camadas horizontais. Cada módulo (auth, catálogo, estoque) continha suas próprias quatro camadas internas: domínio (agregados, entidades, "value objects", interfaces de repositório), aplicação (casos de uso), infraestrutura (implementações de repositório) e apresentação (controladores HTTP ou "handlers" Lambda). Um módulo compartilhado ("shared") forneceu as abstrações base (entidade, exceção, repositório) e configuração de infraestrutura.

A versão monolítica DDD utilizou o "framework" FastAPI com rotas HTTP que delegavam aos casos de uso, repositórios implementados com SQLAlchemy sobre PostgreSQL e execução em servidor "Asynchronous Server Gateway Interface" [ASGI] convencional. O "container" Docker foi limitado a 512 MB de memória, equivalente a configuração das funções Lambda.

A versão em microsserviços DDD utilizou "handlers" AWS Lambda puros, sem adaptador Mangum. Cada função Lambda recebia o evento do API Gateway e delegava ao mesmo caso de uso da versão monolítica. Os repositórios foram implementados com a biblioteca boto3 sobre DynamoDB. Essa decisão arquitetural — Lambda puro em vez de adaptador — foi intencional para demonstrar que a camada de aplicação (casos de uso) era genuinamente agnóstica ao mecanismo de transporte, conforme preconizado por Martin (2017).

A troca de PostgreSQL (monolito) para DynamoDB (microsserviços) demonstrou na prática o "Repository Pattern" descrito por Percival e Gregory (2020): a interface de repositório definida no domínio permaneceu idêntica e apenas a implementação de infraestrutura mudou. Essa decisão também eliminou a necessidade de "NAT Gateway" na AWS, reduzindo custos operacionais.

A injecao de dependência [DI] foi implementada com a biblioteca "dependency-injector", utilizando o padrao de "Composition Root" [CR] (Percival e Gregory, 2020): cada "Bounded Context" possuia um "container" declarativo que era o único ponto do sistema a conhecer as implementações concretas dos repositórios. Os casos de uso recebiam interfaces via construtor e desconheciam se estavam conectados a PostgreSQL, DynamoDB ou repositórios em memória (usados em testes). Essa abordagem foi preferida ao mecanismo Depends() do FastAPI por não acoplar a composição de dependências ao "framework", mantendo as camadas de domínio e aplicação como Python puro.

<!-- TODO: Adicionar diagrama da arquitetura como Figura ao passar para Word.
     Figura 1. Arquitetura do sistema monolítico DDD
     Figura 2. Arquitetura dos microsserviços "serverless" DDD
     Figura 3. Fluxo de eventos entre "Bounded Contexts"
     Fonte: Dados originais da pesquisa -->

**Grupo de controle MVC**

Para isolar o efeito da adocao de DDD sobre as métricas de qualidade e produtividade, implementou-se um grupo de controle com arquitetura MVC tradicional. O monolito MVC expunha exatamente a mesma API é os mesmos comportamentos do monolito DDD, porém com uma estrutura propositalmente simplificada: rotas com "queries" SQL diretas via SQLAlchemy, validação "inline", sem separação em camadas de domínio, aplicação ou infraestrutura, sem interfaces abstratas e sem "container" de injecao de dependência. Todo o código concentrou-se em poucos arquivos (app.py, models.py, schemas.py e quatro módulos de rotas).

A migração do monolito MVC para microsserviços "serverless" seguiu o mesmo procedimento do DDD: cada módulo de rota foi convertido em um serviço Lambda independente com "handlers" puros e repositórios DynamoDB. Diferentemente do DDD, não houve reuso de camadas intermediarias — cada "handler" continha a lógica de negócio, a validação é o acesso ao banco de forma monolítica.

Essa abordagem de grupo de controle permitiu comparações pareadas em todas as dimensoes de interesse: complexidade ciclomática [CC], índice de manutenibilidade [IM], acoplamento entre pacotes, tempo de construcao, tempo de migração e tempo de implementação de "feature" nova.

**Ferramentas e tecnologias**

As principais tecnologias utilizadas no experimento foram:

- Linguagem: Python 3.13
- "Framework" HTTP (monolito): FastAPI
- Computação "serverless": AWS Lambda com API Gateway
- Banco de dados: PostgreSQL 16 (monolito) e DynamoDB (microsserviços)
- Mensageria: Amazon SNS e SQS
- Infraestrutura como código: AWS "Serverless Application Model" [SAM]
- Integração continua: GitHub Actions
- Análise estática: radon 6.0.1 (CC, IM, métricas de Halstead), xenon 0.9.3 ("gate" de qualidade)
- Acoplamento: grimp 3.14 (grafo de "imports", acoplamento aferente [Ca] e eferente [Ce])
- Coesao: cohesion 1.2.0 ("Lack of Cohesion of Methods" [LCOM] invertido)
- Testes de carga: k6 v0.55.0
- Simulação de serviços AWS em testes: moto (emulação local de DynamoDB, SNS e SQS)

**Métricas coletadas**

Para avaliar a migração de forma quantitativa, definiram-se métricas em três dimensoes:

*Qualidade de código.* A CC (McCabe, 1976) foi medida com a ferramenta radon, que atribui graus de A (baixa complexidade, 1 a 5) a F (complexidade muito alta, acima de 40) a cada função ou método. O IM foi calculado conforme a fórmula de Coleman et al. (1994), que combina volume de Halstead (1977), CC e linhas de código em escala de 0 a 100. Valores acima de 85 indicam alta manutenibilidade. O acoplamento aferente (Ca) e eferente (Ce) entre pacotes foi obtido com grimp, que constroi o grafo de "imports" Python e agrupa módulos em pacotes de dois níveis. A instabilidade foi calculada como I = Ce / (Ca + Ce), conforme proposto por Martin (1994). A coesao de classes foi medida com a ferramenta cohesion, que reporta o percentual de atributos acessados pelos métodos de cada classe (inverso do LCOM de Chidamber e Kemerer, 1994). O "gate" de qualidade xenon foi configurado com "thresholds" máximo absoluto C, máximo por módulo B e média A, funcionando como "fitness function" arquitetural (Richards e Ford, 2020).

*Desempenho.* A latência nos percentis p50, p90 e p95 foi medida com a ferramenta k6 em cenário de carga controlada, conforme detalhado no subtópico de teste de carga.

*Produtividade com Inteligência Artificial [IA].* Cada funcionalidade foi implementada pelo agente de IA Claude Code. Para cada implementação registrou-se: tempo total de parede ("wall clock") do início do "prompt" até código funcional com todos os testes aprovados, número de iterações de correção e variação na CC e no IM antes e depois da "feature". A cronometragem foi realizada por "script" próprio que gravava marcações de tempo ("timestamps") no início e no fim de cada tarefa.

<!-- TODO: Inserir Tabela ao passar para Word:
     Tabela 1. Métricas coletadas, ferramentas e dimensoes de avaliação
     Colunas: Dimensao | Métrica | Ferramenta | Unidade
     Fonte: Dados originais da pesquisa -->

**Procedimento experimental**

O desenvolvimento seguiu uma estrategia de "Walking Skeleton" (Newman, 2019): toda a infraestrutura (integração continua, bancos de dados, filas de mensageria e "templates" de implantação) foi provisionada e validada antes de qualquer implementação de lógica de negócio, contendo apenas um "endpoint" de verificação de saude (/health). Essa abordagem isolou o tempo de configuração de infraestrutura do tempo de desenvolvimento de funcionalidades, permitindo medicao precisa da produtividade.

Na fase de construcao do monolito DDD, as funcionalidades foram adicionadas incrementalmente na seguinte ordem: (1) autenticação com "JSON Web Token" [JWT], (2) "Create, Read, Update, Delete" [CRUD] de Categoria, (3) CRUD de Produto com "Value Objects" SKU e Dinheiro, (4) entrada de estoque com criação do segundo BC e (5) saida de estoque. Cada funcionalidade foi implementada em sessão única do agente Claude Code, com cronometragem independente. O tempo total de construcao do monolito DDD foi de 24 minutos e 50 segundos, resultando em 36 testes aprovados e 1821 linhas de código executável [SLOC].

O monolito MVC foi construído com a mesma ferramenta de IA é a mesma especificação de API, porém sem instrucoes de DDD ou separação de camadas. O tempo total foi de aproximadamente 8 minutos, resultando em 33 testes e 466 SLOC.

Na fase de migração para microsserviços, seis agentes Claude Code foram executados em paralelo — três para os serviços DDD (auth, catálogo, estoque) e três para os serviços MVC equivalentes. Cada agente recebeu a tarefa de migrar um módulo do monolito para um serviço Lambda independente, criando "handlers" puros, repositórios DynamoDB e configuração SAM. Os tempos foram cronometrados individualmente por serviço. O tempo somado da migração DDD foi de 12 minutos e 36 segundos; o da migração MVC, 6 minutos e 46 segundos. Todos os 104 testes (52 DDD e 52 MVC) foram aprovados na primeira iteração de cada agente. Os três serviços DDD foram implantados na AWS e validados com teste fim-a-fim em produção; os serviços MVC foram validados apenas localmente.

Por fim, na fase de "feature" nova, uma funcionalidade de alerta de estoque baixo foi especificada e implementada em quatro variantes (monolito DDD, monolito MVC, microsserviço DDD e microsserviço MVC) por quatro agentes em paralelo, cada um partindo de testes pré-escritos. Essa fase permitiu medir o impacto da arquitetura sobre a velocidade de adicao de funcionalidades em bases de código já existentes.

**Contrato de integração e testes-guardiao**

Para garantir que o código gerado pelos agentes de IA funcionasse em ambiente real e não apenas em testes locais, elaborou-se um documento de contrato de integração com seis regras obrigatorias para todos os microsserviços. Esse contrato foi motivado por uma classe recorrente de defeitos em que o código aprovava testes unitarios, porém falhava na implantação por desalinhamento entre variáveis de ambiente do "template" SAM e as lidas pelo código, ou por uso de repositórios em memória como substitutos silenciosos do DynamoDB.

As regras determinaram que: (1) cada "handler" deveria ler exatamente as variáveis de ambiente declaradas no template.yaml, sem variantes inventadas; (2) os testes deveriam utilizar a biblioteca moto para emular DynamoDB, SNS e SQS localmente, em vez de repositórios em memória com desvio condicional; (3) todo teste de escrita deveria verificar a persistência real via boto3; (4) consumidores de eventos deveriam gravar estado no DynamoDB, não apenas registrar mensagens em "log"; (5) nenhuma chamada AWS deveria ocorrer em tempo de importação do módulo; e (6) "handlers" não deveriam capturar exceções genericas.

Para cada serviço, criou-se um arquivo de testes-guardiao (test_integration_contract.py) que parseava o template.yaml automaticamente e falhava caso qualquer variável de ambiente declarada não aparecesse no código-fonte, caso houvesse desvio condicional para repositório em memória ou caso consumidores de eventos não realizassem persistência. Esses quatro testes-guardiao foram executados junto com os testes de comportamento em todas as bases de código. A "fixture" de teste conftest.py, compartilhada por todos os serviços, abria o contexto mock_aws() da moto em modo "autouse", criava as tabelas, tópicos e filas a partir do template.yaml e configurava as variáveis de ambiente com os nomes reais.

**Teste de carga**

A latência em produção foi medida com a ferramenta k6 v0.55.0 em cenário de rampa: 1 a 5 usuarios virtuais [VU] durante 15 segundos de aquecimento, 10 VUs sustentados por 60 segundos e redução gradual em 10 segundos. O fluxo funcional completo foi executado em sequência por cada VU: registrar usuario, efetuar "login", criar categoria, criar produto, consultar estoque, registrar entrada e registrar saida. Esse cenário reproduziu a jornada completa de um operador do sistema.

O monolito DDD foi testado em instância EC2 t3.micro com uma única instância, "Application Load Balancer" [ALB] e banco RDS PostgreSQL. Os microsserviços DDD foram testados com funções Lambda configuradas com 512 MB de memória, API Gateway e DynamoDB no modo de cobranca por requisicao. Ambos os testes foram executados a partir da mesma maquina local, de modo que a latência de rede estivesse incluida de forma equivalente em ambas as medicoes.

---

## Resultados e Discussão

<!-- ================================================================
     REGRAS DESTA SEÇÃO:
     - Pode ter subtópicos (negrito, recuo 1,25cm)
     - Apresentar resultados E interpretar/discutir
     - Figuras: título abaixo, "Fonte: Resultados originais da pesquisa"
     - Tabelas: título acima, "Fonte: Resultados originais da pesquisa"
     ================================================================ -->

**Qualidade de código e manutenibilidade**

A Tabela 2 apresenta os resultados de Complexidade Ciclomática [CC] e Índice de Manutenibilidade [IM] obtidos para as oito bases de código analisadas. Todas as métricas foram extraidas com a ferramenta radon, conforme descrito na secao anterior.

<!-- Tabela 2. Complexidade ciclomática e índice de manutenibilidade por base de código -->
<!-- Fonte: Resultados originais da pesquisa -->

| Base de código | Arquitetura | SLOC | Blocos | CC medio | IM medio |
|----------------|-------------|------|--------|----------|----------|
| Monolito DDD | DDD | 1821 | 228 | 1,84 | 90,28 |
| Monolito MVC | MVC | 466 | 43 | 1,86 | 75,04 |
| Microsserviço Auth | DDD | 344 | 62 | 1,73 | 93,25 |
| Microsserviço Catálogo | DDD | 676 | 94 | 2,31 | 81,89 |
| Microsserviço Estoque | DDD | 685 | 83 | 2,22 | 87,28 |
| Microsserviço Auth | MVC | 103 | 10 | 2,50 | 88,66 |
| Microsserviço Catálogo | MVC | 240 | 20 | 3,90 | 83,13 |
| Microsserviço Estoque | MVC | 257 | 22 | 2,82 | 80,54 |

Todas as bases de código apresentaram CC medio na faixa A (1 a 5) da escala proposta por McCabe (1976), o que indica baixa complexidade por função ou método individual. Contudo, a comparação entre arquiteturas revela diferenças consistentes. A média global de CC das quatro bases DDD foi de 2,03, enquanto a das quatro bases MVC foi de 2,77 — uma diferença de 27%. Esse resultado sugere que a decomposição em camadas é a separação de responsabilidades promovidas pelo DDD produziram funções menores e com menos caminhos de decisão.

A diferença e mais acentuada nos microsserviços de Catálogo, onde o DDD obteve CC de 2,31 contra 3,90 do MVC. No MVC, a lógica de validação, acesso a dados e formatação de resposta concentrou-se em poucos "handlers", elevando o número de ramificações por função. No DDD, a mesma lógica foi distribuída entre entidades de domínio, casos de uso e repositórios, cada um com responsabilidade delimitada.

O IM apresentou diferença ainda mais expressiva. No monolito, o DDD atingiu 90,28 — classificado como alta manutenibilidade segundo a escala de Coleman et al. (1994) — enquanto o MVC obteve 75,04, na faixa moderada. Essa diferença de 15,24 pontos representa o maior delta observado entre todas as comparações pareadas. Nos microsserviços, a diferença se reduziu: o IM medio DDD foi de 87,47 contra 84,11 do MVC, uma diferença de 3,36 pontos. A convergência nos microsserviços pode ser explicada pelo menor tamanho de cada serviço: com menos linhas de código, mesmo o MVC produz arquivos curtos e de baixa complexidade, o que eleva o IM.

O "gate" de qualidade xenon, configurado com "thresholds" máximo absoluto C, máximo por módulo B e média A, foi aprovado por sete das oito bases de código. A única falha ocorreu no microsserviço Catálogo DDD, que possui um "handler" de roteamento com CC superior ao limite B. Essa função concentra o despacho de rotas HTTP para os casos de uso correspondentes e representa um ponto de melhoria identificado pela "fitness function" arquitetural, conforme conceituado por Richards e Ford (2020).

**Acoplamento e coesao**

A análise de acoplamento entre pacotes foi realizada com a ferramenta grimp, que constroi o grafo de "imports" Python e calcula o acoplamento aferente (Ca), eferente (Ce) é a instabilidade (I = Ce / (Ca + Ce)) por pacote, conforme proposto por Martin (1994). A Tabela 3 apresenta os resultados agregados por base de código.

<!-- Tabela 3. Acoplamento entre pacotes e coesao de classes por base de código -->
<!-- Fonte: Resultados originais da pesquisa -->

| Base de código | Arquitetura | Pacotes | Módulos | Instabilidade média | Classes | Coesao média (%) |
|----------------|-------------|---------|---------|---------------------|---------|------------------|
| Monolito DDD | DDD | 6 | 117 | 0,417 | 87 | 32,29 |
| Monolito MVC | MVC | 4 | 5 | 0,000 | 0 | 0,00 |
| Microsserviço Auth | DDD | 6 | 34 | 0,458 | 18 | 28,24 |
| Microsserviço Catálogo | DDD | 5 | 21 | 0,450 | 28 | 48,87 |
| Microsserviço Estoque | DDD | 5 | 35 | 0,450 | 21 | 39,15 |
| Microsserviço Auth | MVC | 1 | 5 | 0,000 | 0 | 0,00 |
| Microsserviço Catálogo | MVC | 1 | 4 | 0,000 | 0 | 0,00 |
| Microsserviço Estoque | MVC | 1 | 5 | 0,000 | 0 | 0,00 |

As bases DDD apresentaram instabilidade média entre 0,417 e 0,458, valores na faixa de equilibrio (0,3 a 0,7) da escala de Martin (1994). Esse resultado reflete a organização em camadas direcionais: os pacotes de apresentação ("handlers") dependem dos pacotes de aplicação, que dependem do domínio, que por sua vez depende apenas do módulo compartilhado. No monolito DDD, por exemplo, o pacote "src.presentation" possui Ce = 4 e Ca = 0 (instabilidade 1,0), pois depende de todos os "Bounded Contexts" sem ser dependência de nenhum. O pacote "src.shared", ao contrario, possui Ca = 4 e Ce = 0 (instabilidade 0,0), configurando-se como o componente mais estável do sistema — exatamente o papel esperado para abstrações base, conforme a regra de inversao de dependência de Martin (2017).

As bases MVC registraram instabilidade 0,000 em todos os pacotes. Esse valor não indica estabilidade superior, mas reflete a impossibilidade de medicao: cada serviço MVC possui apenas um pacote (src.handlers) sem dependências internas entre módulos. A ausência de pacotes com acoplamento aferente e eferente torna a métrica trivial, não informativa. Richards e Ford (2020) observam que a modularidade só pode ser avaliada quando ha fronteiras explícitas entre componentes. No MVC, a ausência dessas fronteiras impede a aplicação de métricas de acoplamento, o que constitui uma limitação estrutural e não uma vantagem arquitetural.

A coesao de classes, medida pela ferramenta cohesion como o percentual medio de atributos acessados pelos métodos de cada classe (inverso do LCOM de Chidamber e Kemerer, 1994), foi mensurável apenas nas bases DDD. Os valores variaram de 28,24% (microsserviço Auth) a 48,87% (microsserviço Catálogo). Essa variação reflete a natureza dos agregados em cada contexto: o Catálogo possui entidades com atributos coesos (Produto referência SKU, Dinheiro e Categoria no mesmo fluxo), enquanto o Auth possui classes de serviço com métodos mais independentes (registrar, autenticar, validar "token").

As bases MVC não possuem classes — toda a lógica e implementada em funções puras nos "handlers" — o que impossibilitou a medicao de coesao. Essa é uma consequência direta da escolha arquitetural: o MVC privilegia funções procedurais, enquanto o DDD organiza o comportamento em torno de objetos de domínio com estado e invariantes.

**Desempenho e latência**

Os resultados do teste de carga com k6 sao apresentados na Tabela 4, que compara a latência por "endpoint" entre o monolito DDD (EC2 t3.micro com ALB) é os microsserviços DDD (Lambda 512 MB com API Gateway).

<!-- Tabela 4. Latência por "endpoint" — monolito DDD vs microsserviços DDD -->
<!-- Fonte: Resultados originais da pesquisa -->

| Endpoint | Alvo | p50 (ms) | p90 (ms) | p95 (ms) | Média (ms) |
|----------|------|----------|----------|----------|------------|
| health | Monolito | 137 | 250 | 253 | 174 |
| health | Microsserviço | 373 | 486 | 501 | 316 |
| registrar | Monolito | 887 | 1323 | 1445 | 913 |
| registrar | Microsserviço | 1530 | 1648 | 1734 | 1532 |
| login | Monolito | 917 | 1311 | 1416 | 896 |
| login | Microsserviço | 1460 | 1517 | 1613 | 1479 |
| criar categoria | Monolito | 147 | 250 | 253 | 177 |
| criar categoria | Microsserviço | 497 | 562 | 651 | 530 |
| criar produto | Monolito | 194 | 252 | 255 | 207 |
| criar produto | Microsserviço | 635 | 739 | 752 | 588 |
| buscar estoque | Microsserviço | 264 | 505 | 530 | 369 |
| entrada estoque | Microsserviço | 426 | 694 | 723 | 489 |
| saida estoque | Microsserviço | 445 | 684 | 746 | 506 |

O monolito apresentou latência de duas a três vezes menor que os microsserviços no percentil 50 para todos os "endpoints" comparáveis. No "endpoint" health, o monolito registrou p50 de 137 ms contra 373 ms dos microsserviços. Nos "endpoints" de CRUD simples (criar categoria e criar produto), o monolito obteve p50 entre 147 e 194 ms, enquanto os microsserviços variaram entre 497 e 635 ms. Essa diferença e explicada pelo "overhead" fixo da cadeia API Gateway e Lambda: cada requisicao precisa atravessar o roteamento do API Gateway, inicializar o contexto da função Lambda (quando ocorre inicialização a frio ou "cold start") e retornar pela mesma cadeia.

Os "endpoints" de autenticação (registrar e "login") foram os mais lentos em ambas as arquiteturas, com p50 entre 887 e 917 ms no monolito e entre 1460 e 1530 ms nos microsserviços. Essa latência elevada e dominada pelo custo computacional do algoritmo bcrypt, utilizado para derivação de senha. O bcrypt e intencionalmente lento — por projeto criptográfico — e consome ciclos de "CPU" proporcionais ao fator de custo configurado. A diferença absoluta entre monolito e microsserviço (~570 ms) permanece na mesma ordem de grandeza do "overhead" observado nos demais "endpoints", sugerindo que o bcrypt adiciona um custo base constante sobre o qual o "overhead" de infraestrutura se soma.

Um resultado relevante foi o comportamento nos percentis superiores. Enquanto o monolito apresentou dispersão significativa entre p50 e p95 — por exemplo, de 887 ms para 1445 ms no "endpoint" registrar, um aumento de 63% — os microsserviços exibiram dispersão menor: de 1530 ms para 1734 ms, aumento de apenas 13%. Esse padrao indica que os microsserviços, apoiados pela escalabilidade horizontal automática do Lambda, oferecem latência mais previsível sob carga, mesmo que a latência absoluta seja maior. O monolito em instância t3.micro, com recursos fixos de CPU e memória, sofre degradação mais acentuada quando multiplos usuarios concorrentes executam operações computacionalmente intensivas como o bcrypt.

**Produtividade assistida por inteligência artificial**

Os tempos de implementação por agente de IA foram registrados em três fases: construcao do monolito (Fase A), migração para microsserviços (Fase B) e implementação de "feature" nova (Fase C). A Tabela 5 consolida os resultados de todas as fases. Antes da leitura da tabela, cabe esclarecer a interpretação das colunas: o tempo na Fase B apresenta-se em duas linhas, "somado" e "paralelo (max)"; a linha "somado" corresponde a soma dos tempos individuais dos três microsserviços, representando o esforco equivalente caso a migração fosse sequencial, enquanto "paralelo (max)" corresponde ao tempo real de parede ("wall clock") observado, uma vez que os três agentes foram disparados simultaneamente é o tempo total equivale ao do serviço mais lento. A coluna Testes, nas fases A e B, apresenta o número absoluto de testes aprovados; na Fase C, adota-se a notação "novos/total", em que o numerador é o número de testes novos adicionados pela feature (quatro em todas as variantes) é o denominador é o número total de testes aprovados após a implementação, incluindo os testes preexistentes — ambos passando, o que evidência ausência de regressao.

<!-- Tabela 5. Tempos de implementação por fase e arquitetura -->
<!-- Fonte: Resultados originais da pesquisa -->

| Fase | Variante | Tempo | Testes | Iterações | SLOC |
|------|----------|-------|--------|-----------|------|
| A — Construcao monolito | DDD | 24min 50s | 36 | 1 por "feature" | 1821 |
| A — Construcao monolito | MVC | ~8min | 33 | 1 | 466 |
| B — Migração (somado) | DDD | 12min 36s | 52/52 | 1 por serviço | — |
| B — Migração (somado) | MVC | 6min 46s | 52/52 | 1 por serviço | — |
| B — Migração (paralelo max) | DDD | 4min 33s | — | — | — |
| B — Migração (paralelo max) | MVC | 2min 31s | — | — | — |
| C — Feature (monolito) | DDD | 3min 31s | 4/40 | 1 | — |
| C — Feature (monolito) | MVC | 1min 53s | 4/37 | 1 | — |
| C — Feature (microsserviço) | DDD | 3min 01s | 4/24 | 1 | — |
| C — Feature (microsserviço) | MVC | 1min 35s | 4/24 | 1 | — |

O padrao mais consistente observado foi a vantagem de velocidade do MVC sobre o DDD em todas as fases. Na construcao do monolito, o DDD demandou 24 minutos e 50 segundos contra aproximadamente 8 minutos do MVC — o MVC foi cerca de três vezes mais rápido. Na migração, o tempo somado do MVC (6 minutos e 46 segundos) foi 46% menor que o do DDD (12 minutos e 36 segundos). Na "feature" nova, o MVC foi 47% mais rápido no monolito (1 minuto e 53 segundos contra 3 minutos e 31 segundos) e também 47% mais rápido no microsserviço (1 minuto e 35 segundos contra 3 minutos e 1 segundo).

Essa diferença de velocidade esta diretamente relacionada ao volume de código e ao número de artefatos que cada arquitetura exige. A implementação DDD requer a criação de entidades de domínio, "value objects", interfaces de repositório, implementações concretas, casos de uso e "schemas" de entrada e saida, distribuídos em multiplos arquivos e camadas. Na "feature" de alerta de estoque baixo, por exemplo, o DDD criou cinco arquivos novos e modificou sete no monolito, enquanto o MVC não criou nenhum arquivo novo e modificou apenas três.

Um aspecto relevante e que todas as doze implementações (cinco "features" do monolito DDD, construcao do monolito MVC, seis migrações e quatro "features" novas) convergiram na primeira iteração do agente de IA, sem necessidade de re-"prompt" ou correção manual. Todos os 104 testes da migração (52 DDD e 52 MVC) é os 16 testes da fase de "feature" nova foram aprovados integralmente. Todos os seis serviços implantados na AWS (três DDD em produção, três MVC validados localmente) funcionaram corretamente na primeira tentativa de implantação. Esse resultado indica que a especificação formal do domínio é os contratos de integração fornecidos como contexto ao agente de IA foram suficientes para guiar a geração de código funcional independentemente da complexidade arquitetural.

Na migração, observou-se que o DDD permite reutilização significativa das camadas de domínio e aplicação. Os casos de uso, entidades e "value objects" permaneceram idênticos entre monolito e microsserviços — apenas a camada de infraestrutura (repositórios e "handlers") foi substituida. Essa propriedade, derivada da regra de dependência da "Clean Architecture" (Martin, 2017), significa que a migração DDD exige reescrever somente a periferia do sistema. No MVC, por outro lado, cada "handler" concentra toda a lógica, de modo que a migração equivale a reescrever o serviço inteiro.

**Comparação DDD vs MVC — síntese**

A Tabela 6 consolida as principais métricas das duas arquiteturas, permitindo uma visao comparativa cruzada das dimensoes analisadas.

<!-- Tabela 6. Comparação cruzada DDD vs MVC nas principais dimensoes -->
<!-- Fonte: Resultados originais da pesquisa -->

| Dimensao | Métrica | DDD | MVC | Observação |
|----------|---------|-----|-----|------------|
| Tamanho | SLOC (monolito) | 1821 | 466 | DDD ~3,9x maior |
| Complexidade | CC medio (global) | 2,03 | 2,77 | DDD 27% menor |
| Manutenibilidade | IM medio (global) | 88,18 | 81,84 | DDD 6,3 pontos maior |
| Manutenibilidade | IM (monolito) | 90,28 | 75,04 | DDD 15,2 pontos maior |
| Acoplamento | Instabilidade média | 0,44 | 0,00 | MVC não mensurável |
| Coesao | Coesao média (%) | 28-49 | 0 | MVC sem classes |
| Latência | p50 CRUD (ms) | 147-194 | — | Monolito DDD |
| Latência | p50 CRUD (ms) | 497-635 | — | Microsserviço DDD |
| Produtividade | Construcao monolito | 24min 50s | ~8min | MVC ~3x mais rápido |
| Produtividade | Migração somada | 12min 36s | 6min 46s | MVC 46% mais rápido |
| Produtividade | Feature monolito | 3min 31s | 1min 53s | MVC 47% mais rápido |
| Qualidade | Xenon (gate) | 3/4 PASS | 4/4 PASS | DDD 1 falha (Catálogo) |

Os resultados revelam um "trade-off" claro entre as duas abordagens. O DDD produziu código com menor complexidade ciclomática e maior manutenibilidade, especialmente no monolito, onde a diferença de IM atingiu 15 pontos. Além disso, somente o DDD permitiu a medicao de acoplamento entre pacotes e coesao de classes, o que torna as propriedades arquiteturais visiveis e monitoráveis por ferramentas automatizadas. Essa visibilidade e essencial para a prática de "fitness functions" arquiteturais, conforme defendido por Richards e Ford (2020), que propoe a validação continua de propriedades estruturais como parte do ciclo de desenvolvimento.

Em contrapartida, o MVC foi consistentemente mais rápido em todas as fases de desenvolvimento e produziu significativamente menos código. A diferença de velocidade (46 a 53% na migração e "feature" nova) pode ser decisiva em cenários onde o tempo de entrega é a restrição predominante é o domínio de negócio e suficientemente simples para dispensar separação explícita de camadas.

E relevante observar que a complexidade ciclomática do MVC, embora maior, permaneceu na faixa A em quase todas as bases de código, com exceção do microsserviço Catálogo MVC (CC = 3,90, ainda na faixa A). A diferença entre as arquiteturas, portanto, não se manifesta como defeito de qualidade no MVC, mas como ausência de estrutura para evolução: a medida que o domínio cresce, a concentração de lógica em poucos arquivos tende a elevar a CC de forma mais acentuada do que a distribuicao em camadas do DDD.

**Limitações**

Os resultados devem ser interpretados considerando as seguintes limitações do estudo. Primeiro, o domínio modelado e relativamente simples, com três "Bounded Contexts", 1821 SLOC no monolito DDD e apenas onze termos na Linguagem Ubíqua. Domínios empresariais reais tendem a ser significativamente mais complexos, é os beneficios do DDD podem ser mais pronunciados — ou os custos mais elevados — em escala maior.

Segundo, o teste de carga foi conduzido com no máximo 10 usuarios virtuais e duração de 60 segundos em regime sustentado. Esse cenário e insuficiente para extrapolar conclusões sobre comportamento em produção com centenas ou milhares de usuarios concorrentes. Aspectos como inicialização a frio ("cold start") em escala, exaustao de conexões e limites de concorrência do Lambda não foram exercitados.

Terceiro, os resultados de produtividade sao inerentemente dependentes do agente de IA utilizado (Claude Code), da versão do modelo, do contexto fornecido e da formulação do "prompt". Embora todas as implementações tenham sido realizadas com o mesmo modelo e formato de instrucoes, não ha garantia de que uma repetição do experimento produziria tempos idênticos. A variabilidade estocástica dos modelos de linguagem é uma limitação metodológica conhecida.

Quarto, o mesmo desenvolvedor elaborou as especificações, os "prompts" é os contratos de integração para ambas as arquiteturas, o que pode introduzir vies favorável ao DDD — a arquitetura escolhida como foco do estudo. A mitigação desse risco foi feita pela utilização do mesmo agente de IA para todas as implementações e pela padronização dos contratos de API.

Por fim, as métricas de análise estática capturam aspectos estruturais do código, mas não abrangem todas as dimensoes de qualidade de "software". Propriedades como legibilidade, adequação ao domínio, facilidade de "debugging" e custo de integração de novos desenvolvedores não foram avaliadas neste estudo.

---

## Conclusão

A migração de um monolito para microsserviços "serverless" utilizando DDD e "Clean Architecture" mostrou-se viável e produziu melhorias mensuráveis na qualidade estrutural do código. O objetivo principal do trabalho — avaliar quantitativamente o impacto dessa migração por meio de métricas de qualidade, desempenho e produtividade assistida por IA — foi atendido nas três dimensoes propostas.

O DDD produziu código com CC 27% menor e IM 6,3 pontos superior ao MVC na média global das oito bases de código. No monolito, onde a diferença de IM atingiu 15,2 pontos (90,28 contra 75,04), a vantagem foi mais expressiva. Além disso, somente o DDD permitiu a medicao de acoplamento entre pacotes e coesao de classes, tornando as propriedades arquiteturais visiveis para monitoramento automatizado. O MVC, por não possuir fronteiras explícitas entre componentes, inviabilizou a aplicação dessas métricas.

O "Repository Pattern" demonstrou na prática sua função de desacoplamento entre domínio e infraestrutura. A troca de PostgreSQL para DynamoDB durante a migração exigiu apenas a substituicao das implementações concretas de repositório, sem alteração nas camadas de domínio e aplicação. Essa propriedade, derivada da regra de dependência da "Clean Architecture", reduziu o escopo da migração DDD as camadas perifericas do sistema.

A comunicação assincrona via SNS e SQS entre "Bounded Contexts" garantiu desacoplamento total entre os microsserviços de Catálogo e Estoque. O mecanismo de projeção local permitiu que cada serviço operasse de forma autônoma, sem dependência sincrona de outros contextos. O fluxo completo — da criação de produto até a consulta de estoque com saldo atualizado — foi validado em produção com sucesso.

O "trade-off" entre DDD e MVC revelou-se consistente em todas as fases do experimento. O MVC foi entre 46% e três vezes mais rápido na construcao e migração, com volume de código significativamente menor (466 contra 1821 SLOC no monolito). Em contrapartida, o MVC concentrou lógica em poucos arquivos, o que tende a elevar a CC de forma mais acentuada a medida que o domínio cresce. A escolha entre as duas abordagens depende, portanto, do horizonte de evolução do sistema: para domínios simples e ciclos de entrega curtos, o MVC oferece vantagem em velocidade; para domínios complexos com expectativa de evolução continua, o DDD oferece estrutura que preserva a manutenibilidade ao longo do tempo.

A produtividade com agentes de IA foi elevada em ambas as arquiteturas. Todas as doze implementações convergiram na primeira iteração, com 100% dos testes aprovados e todos os serviços funcionais na primeira tentativa de implantação. Esse resultado, porém, dependeu criticamente da qualidade dos artefatos fornecidos como contexto: especificação formal do domínio, contratos de API e, sobretudo, o contrato de integração com testes-guardiao. A ausência inicial desse contrato havia produzido código que passava em testes locais mas falhava na implantação; sua introdução elevou a taxa de sucesso de implantação de 33% para 100%. Conclui-se que a eficacia da geração de código por IA esta condicionada a existência de especificações formais e mecanismos de verificação automatizada que constranjam a saida do modelo.

Em termos de desempenho, os microsserviços apresentaram latência de duas a três vezes maior que o monolito no percentil 50, em razão do "overhead" fixo da cadeia API Gateway e Lambda. Contudo, os microsserviços exibiram dispersão menor entre p50 e p95, indicando latência mais previsível sob carga. Esse resultado sugere que a decisão entre monolito e microsserviços "serverless" deve considerar não apenas a latência absoluta, mas também a previsibilidade é a capacidade de escalabilidade automática.

O estudo possui limitações que restringem a generalização dos resultados: o domínio modelado e simples (três "Bounded Contexts", 1821 SLOC), o teste de carga foi conduzido com no máximo 10 usuarios virtuais é os resultados de produtividade sao dependentes do agente de IA, do modelo e do contexto fornecido.

Como trabalhos futuros, sugere-se: (1) a replicação do experimento em domínios de maior complexidade, com dezenas de "Bounded Contexts" e equipes multiplas, para verificar se os beneficios do DDD se ampliam proporcionalmente; (2) a comparação entre diferentes modelos de IA e configurações de "prompt" para quantificar a variabilidade estocástica na geração de código; (3) a aplicação de técnicas de engenharia do caos para avaliar a resiliência dos microsserviços sob condições de falha; e (4) a análise de custo operacional em cenários de carga real prolongada, incluindo aspectos como inicialização a frio em escala e limites de concorrência do Lambda.

---

## Agradecimento

<!-- Opcional, máximo 3 linhas -->

[PREENCHER SE DESEJADO]

---

## Referências

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

Ford, N.; Richards, M.; Sadalage, P.; Dehghani, Z. 2022. Software Architecture: The Hard Parts. 1ed. O'Reilly Média, Sebastopol, CA, USA.

Halstead, M.H. 1977. Elements of Software Science. 1ed. Elsevier, New York, NY, USA.

Martin, R.C. 1994. OO Design Quality Metrics: An Analysis of Dependencies. Object Mentor, Gurnee, IL, USA.

Martin, R.C. 2017. Clean Architecture: A Craftsman's Guide to Software Structure and Design. 1ed. Prentice Hall, Upper Saddle River, NJ, USA.

McCabe, T.J. 1976. A complexity measure. IEEE Transactions on Software Engineering SE-2(4): 308-320.

Newman, S. 2019. Monolith to Microservices: Evolutionary Patterns to Transform Your Monolith. 1ed. O'Reilly Média, Sebastopol, CA, USA.

Newman, S. 2021. Building Microservices: Designing Fine-Grained Systems. 2ed. O'Reilly Média, Sebastopol, CA, USA.

Percival, H.; Gregory, B. 2020. Architecture Patterns with Python: Enabling Test-Driven Development, Domain-Driven Design, and Event-Driven Microservices. 1ed. O'Reilly Média, Sebastopol, CA, USA.

Richards, M.; Ford, N. 2020. Fundamentals of Software Architecture: An Engineering Approach. 1ed. O'Reilly Média, Sebastopol, CA, USA.

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
