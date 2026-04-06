# Feature 5: Eventos de Dominio (Microsservicos)

## Contexto

Leia estes arquivos antes de implementar:
- `docs/features/RULES.md` — regras obrigatorias (violacoes sao CRITICAL)
- `docs/architecture.md` — padrao DDD, camadas, container DI (dependency-injector)
- `microsservicos/CLAUDE.md` — regras do projeto
- `docs/spec.md` secoes 1-7 — dominio, agregados, VOs, erros, eventos

Pre-requisito: Features 0-4 ja implementadas nos microsservicos.

**NOTA:** Esta feature so se aplica aos microsservicos. No monolito, a comunicacao entre Catalogo e Estoque e sincrona (in-process) e ja foi implementada na Feature 2.

## O que implementar

Comunicacao assincrona entre Catalogo e Estoque via SNS/SQS:
1. Catalogo publica evento ProdutoCriado no SNS ao criar produto
2. Estoque consome evento via SQS e cria ItemEstoque com saldo=0
3. Catalogo publica ProdutoAtualizado ao atualizar
4. Estoque atualiza projecao local
5. Catalogo publica ProdutoDesativado ao desativar
6. Estoque marca item como inativo

## Eventos

### ProdutoCriado
```json
{
  "evento": "ProdutoCriado",
  "timestamp": "2026-04-05T10:00:00Z",
  "dados": {
    "produto_id": "uuid",
    "sku": "ELET-001",
    "nome": "Teclado Mecanico",
    "categoria_nome": "Eletronicos",
    "preco": 299.90
  }
}
```

### ProdutoAtualizado
```json
{
  "evento": "ProdutoAtualizado",
  "timestamp": "2026-04-05T11:00:00Z",
  "dados": {
    "produto_id": "uuid",
    "sku": "ELET-001",
    "nome": "Teclado Mecanico RGB",
    "categoria_nome": "Eletronicos",
    "preco": 349.90
  }
}
```

### ProdutoDesativado
```json
{
  "evento": "ProdutoDesativado",
  "timestamp": "2026-04-05T12:00:00Z",
  "dados": {
    "produto_id": "uuid"
  }
}
```

## Regras de negocio

1. Eventos sao publicados APOS persistencia bem-sucedida do produto
2. Eventos sao idempotentes (reprocessar nao duplica ItemEstoque)
3. Consumer no Estoque cria/atualiza projecao local (sku, nome_produto, categoria_nome)
4. ProdutoDesativado marca ItemEstoque como inativo
5. Evento com formato invalido deve ser logado e descartado (nao quebra o consumer)

## Testes esperados (3)

```
test_evento_produto_criado_cria_item
  Simular evento ProdutoCriado como SQS record → invocar consumer handler
  Verificar que ItemEstoque foi criado com saldo=0 no DynamoDB

test_evento_idempotente
  Enviar mesmo evento ProdutoCriado duas vezes → consumer processa ambos
  Verificar que existe apenas 1 ItemEstoque (nao duplicou)

test_evento_produto_atualizado
  Criar item via evento ProdutoCriado → enviar ProdutoAtualizado com nome novo
  Verificar que nome_produto foi atualizado na projecao local
```

## Arquivos a modificar (microsservicos)

```
catalogo-service/src/
├── application/use_cases/criar_produto.py    # Adicionar publicacao no SNS apos salvar
├── infrastructure/
│   └── event_publisher.py                    # NOVO — publica no SNS via boto3

estoque-service/src/
├── presentation/handlers/event_consumer.py   # Implementar logica real
├── application/use_cases/
│   ├── criar_item_estoque.py                 # NOVO — cria item a partir de evento
│   └── atualizar_projecao.py                 # NOVO — atualiza nome/categoria
```

## Criterio de pronto

- [ ] 3 testes passam
- [ ] Consumer nao quebra com evento invalido
- [ ] Reprocessar mesmo evento nao duplica dados
- [ ] Catalogo nao importa nada do Estoque (desacoplamento total)
