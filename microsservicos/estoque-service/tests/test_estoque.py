import json
from uuid import uuid4

import pytest

from src.container import EstoqueContainer
from tests.fakes import FakeItemEstoqueRepository, FakeMovimentacaoRepository
from src.domain.entities.item_estoque import ItemEstoque


@pytest.fixture
def container():
    c = EstoqueContainer(
        itens_estoque_table="test-itens-estoque",
        movimentacoes_table="test-movimentacoes",
    )
    c.item_estoque_repository.override(FakeItemEstoqueRepository())
    c.movimentacao_repository.override(FakeMovimentacaoRepository())
    return c


def _make_event(
    method: str,
    path: str,
    body: dict | None = None,
    query: dict | None = None,
) -> dict:
    event = {
        "httpMethod": method,
        "path": path,
        "queryStringParameters": query,
    }
    if body is not None:
        event["body"] = json.dumps(body)
    return event


def _call_handler(container, event: dict) -> dict:
    import src.presentation.handlers.estoque as handler_mod
    original = handler_mod.container
    handler_mod.container = container
    try:
        return handler_mod.handler(event, None)
    finally:
        handler_mod.container = original


def _make_sqs_event(evento: str, dados: dict) -> dict:
    sns_message = json.dumps({"evento": evento, "dados": dados})
    return {
        "Records": [
            {"body": json.dumps({"Message": sns_message})}
        ]
    }


def _call_consumer(container, event: dict) -> dict:
    import src.presentation.handlers.event_consumer as consumer_mod
    original = consumer_mod.container
    consumer_mod.container = container
    try:
        return consumer_mod.handler(event, None)
    finally:
        consumer_mod.container = original


def _criar_item(container) -> ItemEstoque:
    """Helper: cria um ItemEstoque direto no repo fake."""
    item = ItemEstoque(
        produto_id=uuid4(),
        sku="ELET-001",
        nome_produto="Teclado Mecanico",
        categoria_nome="Eletronicos",
        saldo=0,
        ativo=True,
    )
    repo = container.item_estoque_repository()
    repo.save(item)
    return item


def _criar_item_via_handler(container, item: ItemEstoque, quantidade: int) -> dict:
    """Helper: registra entrada via handler."""
    event = _make_event(
        "POST",
        f"/api/v1/estoque/{item.id}/entrada",
        {"quantidade": quantidade},
    )
    return _call_handler(container, event)


# ============================================================
# Entrada (4 testes)
# ============================================================

class TestRegistrarEntrada:
    def test_registrar_entrada(self, container):
        item = _criar_item(container)
        event = _make_event(
            "POST",
            f"/api/v1/estoque/{item.id}/entrada",
            {"quantidade": 10, "lote": "L001"},
        )
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 201
        data = json.loads(resp["body"])
        assert data["tipo"] == "ENTRADA"
        assert data["quantidade"] == 10

    def test_saldo_apos_entrada(self, container):
        item = _criar_item(container)
        _criar_item_via_handler(container, item, 15)
        event = _make_event("GET", f"/api/v1/estoque/{item.id}")
        resp = _call_handler(container, event)
        data = json.loads(resp["body"])
        assert data["saldo"] == 15

    def test_entrada_quantidade_invalida(self, container):
        item = _criar_item(container)
        event = _make_event(
            "POST",
            f"/api/v1/estoque/{item.id}/entrada",
            {"quantidade": -5},
        )
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 400
        data = json.loads(resp["body"])
        assert data["code"] == "ESTOQUE_QUANTIDADE_INVALIDA"

    def test_entrada_item_inexistente(self, container):
        fake_id = str(uuid4())
        event = _make_event(
            "POST",
            f"/api/v1/estoque/{fake_id}/entrada",
            {"quantidade": 10},
        )
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 404
        data = json.loads(resp["body"])
        assert data["code"] == "ESTOQUE_ITEM_NAO_ENCONTRADO"


# ============================================================
# Consultas (3 testes)
# ============================================================

class TestConsultas:
    def test_listar_itens_estoque(self, container):
        _criar_item(container)
        _criar_item(container)
        event = _make_event("GET", "/api/v1/estoque")
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert len(data) == 2

    def test_buscar_item_por_produto(self, container):
        item = _criar_item(container)
        event = _make_event("GET", f"/api/v1/estoque/produto/{item.produto_id}")
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert data["produto_id"] == str(item.produto_id)

    def test_historico_movimentacoes(self, container):
        item = _criar_item(container)
        _criar_item_via_handler(container, item, 10)
        _criar_item_via_handler(container, item, 5)
        event = _make_event("GET", f"/api/v1/estoque/{item.id}/movimentacoes")
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 200
        data = json.loads(resp["body"])
        assert len(data) == 2


# ============================================================
# Saida (3 testes)
# ============================================================

class TestRegistrarSaida:
    def test_registrar_saida(self, container):
        item = _criar_item(container)
        _criar_item_via_handler(container, item, 20)
        event = _make_event(
            "POST",
            f"/api/v1/estoque/{item.id}/saida",
            {"quantidade": 5, "motivo": "Venda"},
        )
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 201
        data = json.loads(resp["body"])
        assert data["tipo"] == "SAIDA"
        assert data["quantidade"] == 5

    def test_saida_estoque_insuficiente(self, container):
        item = _criar_item(container)
        event = _make_event(
            "POST",
            f"/api/v1/estoque/{item.id}/saida",
            {"quantidade": 10},
        )
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 400
        data = json.loads(resp["body"])
        assert data["code"] == "ESTOQUE_INSUFICIENTE"

    def test_saida_zera_estoque(self, container):
        item = _criar_item(container)
        _criar_item_via_handler(container, item, 10)
        event = _make_event(
            "POST",
            f"/api/v1/estoque/{item.id}/saida",
            {"quantidade": 10},
        )
        resp = _call_handler(container, event)
        assert resp["statusCode"] == 201
        # Verify saldo is 0
        get_event = _make_event("GET", f"/api/v1/estoque/{item.id}")
        get_resp = _call_handler(container, get_event)
        data = json.loads(get_resp["body"])
        assert data["saldo"] == 0


# ============================================================
# Multiplas movimentacoes (1 teste)
# ============================================================

class TestMultiplasMovimentacoes:
    def test_multiplas_movimentacoes(self, container):
        item = _criar_item(container)
        _criar_item_via_handler(container, item, 20)
        _criar_item_via_handler(container, item, 10)
        # saida
        event = _make_event(
            "POST",
            f"/api/v1/estoque/{item.id}/saida",
            {"quantidade": 5},
        )
        _call_handler(container, event)
        # check saldo
        get_event = _make_event("GET", f"/api/v1/estoque/{item.id}")
        resp = _call_handler(container, get_event)
        data = json.loads(resp["body"])
        assert data["saldo"] == 25  # 20 + 10 - 5
        # check movimentacoes
        mov_event = _make_event("GET", f"/api/v1/estoque/{item.id}/movimentacoes")
        mov_resp = _call_handler(container, mov_event)
        mov_data = json.loads(mov_resp["body"])
        assert len(mov_data) == 3


# ============================================================
# Eventos (3 testes)
# ============================================================

class TestEventos:
    def test_evento_produto_criado_cria_item(self, container):
        produto_id = str(uuid4())
        event = _make_sqs_event("ProdutoCriado", {
            "produto_id": produto_id,
            "sku": "ELET-001",
            "nome": "Teclado Mecanico",
            "categoria_nome": "Eletronicos",
            "preco": 299.90,
        })
        resp = _call_consumer(container, event)
        assert resp["statusCode"] == 200
        # verify item was created
        repo = container.item_estoque_repository()
        from uuid import UUID
        item = repo.get_by_produto_id(UUID(produto_id))
        assert item is not None
        assert item.saldo == 0
        assert item.nome_produto == "Teclado Mecanico"

    def test_evento_idempotente(self, container):
        produto_id = str(uuid4())
        event = _make_sqs_event("ProdutoCriado", {
            "produto_id": produto_id,
            "sku": "ELET-002",
            "nome": "Mouse",
            "categoria_nome": "Eletronicos",
            "preco": 99.90,
        })
        _call_consumer(container, event)
        _call_consumer(container, event)
        # verify only 1 item exists
        repo = container.item_estoque_repository()
        items = repo.list_filtered()
        items_for_product = [i for i in items if str(i.produto_id) == produto_id]
        assert len(items_for_product) == 1

    def test_evento_produto_atualizado(self, container):
        produto_id = str(uuid4())
        # First create via event
        create_event = _make_sqs_event("ProdutoCriado", {
            "produto_id": produto_id,
            "sku": "ELET-003",
            "nome": "Teclado",
            "categoria_nome": "Eletronicos",
            "preco": 199.90,
        })
        _call_consumer(container, create_event)
        # Then update via event
        update_event = _make_sqs_event("ProdutoAtualizado", {
            "produto_id": produto_id,
            "sku": "ELET-003",
            "nome": "Teclado Mecanico RGB",
            "categoria_nome": "Perifericos",
            "preco": 349.90,
        })
        _call_consumer(container, update_event)
        # verify updated
        repo = container.item_estoque_repository()
        from uuid import UUID
        item = repo.get_by_produto_id(UUID(produto_id))
        assert item.nome_produto == "Teclado Mecanico RGB"
        assert item.categoria_nome == "Perifericos"
