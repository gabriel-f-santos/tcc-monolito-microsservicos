# Feature: Alerta de Estoque Baixo

## Resumo

Cada item de estoque pode ter um limite minimo (`estoque_minimo`). Quando uma
saida faz o saldo cair abaixo desse limite, um alerta e criado automaticamente.
Alertas sao consultaveis via API.

## Endpoints

### Configurar alerta
```
PATCH /api/v1/estoque/{id}/configurar-alerta
Body: {"estoque_minimo": 10}
Response: 200 + item atualizado com campo estoque_minimo
```

### Listar alertas de um item
```
GET /api/v1/estoque/{id}/alertas
Response: 200 + lista de alertas
```

## Regras de negocio

1. `estoque_minimo` deve ser >= 0 (422 se negativo)
2. Ao registrar uma **saida**, se `saldo - quantidade < estoque_minimo`, criar alerta automaticamente
3. Alerta contem: `id`, `item_estoque_id`, `tipo` ("ESTOQUE_BAIXO"), `saldo_atual`, `estoque_minimo`, `criado_em`
4. Se `estoque_minimo` nao foi configurado (null/0), nenhum alerta e gerado
5. Multiplas saidas abaixo do limite geram multiplos alertas (um por saida)
6. Item inexistente → 404

## Modelo do Alerta

```python
{
    "id": "uuid",
    "item_estoque_id": "uuid",
    "tipo": "ESTOQUE_BAIXO",
    "saldo_atual": 5,
    "estoque_minimo": 10,
    "criado_em": "2026-04-12T..."
}
```

## Impacto por arquitetura

### Monolito DDD
- Domain: novo campo `estoque_minimo` no agregado `ItemEstoque`, novo entity `AlertaEstoque`
- Application: novo use case `ConfigurarAlertaUseCase`, logica de criacao de alerta no `RegistrarSaidaUseCase` (ou no metodo `registrar_saida` do agregado)
- Infrastructure: novo repo/model SQLAlchemy `AlertaEstoqueRepository`
- Presentation: novas rotas + schema

### Monolito MVC
- Novo model SQLAlchemy `AlertaEstoque`, novo campo `estoque_minimo` no model `ItemEstoque`
- Novas rotas inline

### Microsservico DDD (estoque-service)
- Mesmo que monolito DDD mas com DynamoDB repo em vez de SQLAlchemy
- Nova tabela DynamoDB `AlertasTable` no template.yaml (ou reusar tabela existente)
- Env var: `ALERTAS_TABLE` (se tabela separada)

### Microsservico MVC (estoque-service-mvc)
- Novas queries DynamoDB inline no handler
- Mesma tabela ou nova

## Testes (4 por variante)

| # | Teste | Comportamento esperado |
|---|-------|----------------------|
| 1 | test_configurar_alerta | PATCH configurar-alerta com estoque_minimo=10 → 200 |
| 2 | test_alerta_criado_quando_saldo_abaixo_minimo | Config min=10, entrada 15, saida 10 → saldo=5, 1 alerta com saldo_atual=5 |
| 3 | test_sem_alerta_quando_saldo_acima_minimo | Config min=5, entrada 20, saida 10 → saldo=10, 0 alertas |
| 4 | test_listar_alertas_multiplos | Config min=10, entrada 20, saida 8, saida 8 → 2 alertas (saldo=12→4, ambos < 10) |
