# Task: Implementar Alerta de Estoque Baixo

## Spec

Leia `docs/features/spec-alerta-estoque-baixo.md` para entender a feature completa.

## Prompt generico (copiar e colar, ajustando o alvo)

```
Implemente a feature "Alerta de Estoque Baixo" para que os 4 testes em
test_alerta_estoque.py passem.

=== CRONOMETRAGEM OBRIGATORIA ===
PRIMEIRA ACAO (antes de ler qualquer arquivo):
  cd /home/gabriel/Documents/tcc/project
  bash scripts/migration-timer.sh start <TIMER_NAME>

ULTIMA ACAO (apos todos os testes passarem):
  cd /home/gabriel/Documents/tcc/project
  bash scripts/migration-timer.sh end <TIMER_NAME>

Substitua <TIMER_NAME> pelo valor da variante (ver secao abaixo).
Se voce nao executar o timer, a medicao do TCC e perdida.
===

ANTES DE CODAR:
1. Leia docs/features/spec-alerta-estoque-baixo.md — spec completa.
2. Leia os testes em test_alerta_estoque.py — comportamento esperado.
3. Entenda o codigo existente do estoque antes de adicionar.

A feature adiciona:
- Campo `estoque_minimo` no ItemEstoque (default 0)
- Endpoint PATCH /{id}/configurar-alerta → seta estoque_minimo
- Endpoint GET /{id}/alertas → lista alertas
- Logica: ao registrar saida, se saldo < estoque_minimo ��� cria alerta automaticamente
- Alerta tem: id, item_estoque_id, tipo="ESTOQUE_BAIXO", saldo_atual, estoque_minimo, criado_em

NAO quebre testes existentes. Os testes anteriores devem continuar passando.

Setup: ativar venv existente e rodar pytest
Rodar: pytest tests/ -v

NAO faca git commit — o orquestrador cuida.
```

## Testes que devem passar (4 novos por variante)

| # | Teste | Comportamento |
|---|-------|-------------|
| 1 | test_configurar_alerta | PATCH configurar-alerta estoque_minimo=10 → 200 |
| 2 | test_alerta_criado_quando_saldo_abaixo_minimo | Config min=10, entrada 15, saida 10 → saldo=5, 1 alerta |
| 3 | test_sem_alerta_quando_saldo_acima_minimo | Config min=5, entrada 20, saida 10 → saldo=10, 0 alertas |
| 4 | test_listar_alertas_multiplos | Config min=10, entrada 20, saida 8, saida 8 → 1 alerta (saldo=4) |

---

## Variante 1: Monolito DDD

**Diretorio:** `monolito/`
**Testes:** `tests/integration/test_alerta_estoque.py` (pre-escrito, 4 testes)
**Timer:** `bash scripts/migration-timer.sh start feat-monolito-ddd` / `end feat-monolito-ddd`

O que implementar:
- `src/estoque/domain/entities/alerta_estoque.py` — entidade AlertaEstoque
- Adicionar campo `estoque_minimo: int = 0` ao agregado `ItemEstoque`
- Logica no metodo `registrar_saida()` ou no use case: se saldo < estoque_minimo, criar AlertaEstoque
- `src/estoque/domain/repositories/alerta_estoque_repository.py` — interface
- `src/estoque/infrastructure/repositories/sqlalchemy_alerta_estoque_repository.py` — implementacao
- `src/estoque/application/use_cases/configurar_alerta.py` — use case
- `src/estoque/presentation/routes/estoque.py` — novas rotas
- Registrar model no conftest.py se necessario (import do model)

Meta: `pytest tests/ -v` → todos os testes existentes + 4 novos passam

---

## Variante 2: Monolito MVC

**Diretorio:** `monolito-mvc/`
**Testes:** `tests/test_alerta_estoque.py` (pre-escrito, 4 testes)
**Timer:** `bash scripts/migration-timer.sh start feat-monolito-mvc` / `end feat-monolito-mvc`

O que implementar:
- Novo model SQLAlchemy `AlertaEstoque` em `models.py`
- Adicionar coluna `estoque_minimo` ao model `ItemEstoque`
- Novas rotas em `routes/estoque.py`: PATCH configurar-alerta + GET alertas
- Logica inline na rota de saida: se saldo < estoque_minimo, criar alerta

Meta: `pytest tests/ -v` → todos os testes existentes + 4 novos passam

---

## Variante 3: Microsservico Estoque DDD

**Diretorio:** `microsservicos/estoque-service/`
**Testes:** `tests/test_alerta_estoque.py` (pre-escrito, 4 testes)
**Timer:** `bash scripts/migration-timer.sh start feat-micro-ddd` / `end feat-micro-ddd`

O que implementar:
- Domain: campo `estoque_minimo` no agregado, entidade AlertaEstoque
- Application: use case configurar alerta
- Infrastructure: DynamoDBAlertaEstoqueRepository (nova tabela ou scan na existente)
- Handler: novas rotas no roteamento de `src/handlers/estoque.py`
- Se usar tabela nova: adicionar ao template.yaml + env var `ALERTAS_TABLE`

IMPORTANTE: testes rodam com moto via conftest.py. Se criar tabela nova no
template.yaml, o conftest ja a cria automaticamente. Sem InMemory fallback.

Meta: `pytest tests/ -v` → 20 existentes + 4 novos = 24 passam

---

## Variante 4: Microsservico Estoque MVC

**Diretorio:** `microsservicos/estoque-service-mvc/`
**Testes:** `tests/test_alerta_estoque.py` (pre-escrito, 4 testes)
**Timer:** `bash scripts/migration-timer.sh start feat-micro-mvc` / `end feat-micro-mvc`

O que implementar:
- Novas rotas no handler `src/handlers/estoque.py`: PATCH configurar-alerta + GET alertas
- Campo `estoque_minimo` no item (update_item no DynamoDB)
- Logica inline na saida: se saldo < estoque_minimo, put_item alerta
- Se usar tabela nova: adicionar ao template.yaml + env var

IMPORTANTE: testes rodam com moto via conftest.py. Sem InMemory fallback.
Usar os.environ["ALERTAS_TABLE"] (se tabela nova) dentro de funcao, nao em modulo.

Meta: `pytest tests/ -v` → 20 existentes + 4 novos = 24 passam

---

## Checklist de done (todas as variantes)

- [ ] Timer start executado como primeira acao
- [ ] `pytest tests/ -v` → todos passam (existentes + 4 novos)
- [ ] Testes existentes NAO quebraram
- [ ] Timer end executado como ultima acao
- [ ] NAO fez git commit (orquestrador cuida)
