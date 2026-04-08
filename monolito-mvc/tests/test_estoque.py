"""Estoque tests — mesmos payloads e respostas do monolito DDD."""
import uuid
from tests.conftest import _register_and_login, _auth_header


def _setup_produto(client, token):
    """Cria categoria + produto + retorna item_estoque_id."""
    cat = client.post("/api/v1/categorias",
        json={"nome": f"EstCat-{uuid.uuid4().hex[:6]}"},
        headers=_auth_header(token),
    ).json()
    prod = client.post("/api/v1/produtos",
        json={"sku": f"EST-{uuid.uuid4().hex[:6]}", "nome": "Item", "preco": 10, "categoria_id": cat["id"]},
        headers=_auth_header(token),
    ).json()
    item = client.get(f"/api/v1/estoque/produto/{prod['id']}", headers=_auth_header(token)).json()
    return item["id"]


# --- Entrada ---

def test_registrar_entrada(client):
    """POST /estoque/{id}/entrada → 201 + movimentacao ENTRADA."""
    token = _register_and_login(client)
    item_id = _setup_produto(client, token)
    response = client.post(f"/api/v1/estoque/{item_id}/entrada",
        json={"quantidade": 100, "lote": "NF-001", "motivo": "Recebimento"},
        headers=_auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tipo"] == "ENTRADA"
    assert data["quantidade"] == 100


def test_saldo_apos_entrada(client):
    """Entrada 100 + Entrada 50 → saldo=150."""
    token = _register_and_login(client)
    item_id = _setup_produto(client, token)
    client.post(f"/api/v1/estoque/{item_id}/entrada",
        json={"quantidade": 100}, headers=_auth_header(token))
    client.post(f"/api/v1/estoque/{item_id}/entrada",
        json={"quantidade": 50}, headers=_auth_header(token))
    response = client.get(f"/api/v1/estoque/{item_id}", headers=_auth_header(token))
    assert response.json()["saldo"] == 150


def test_entrada_quantidade_invalida(client):
    """POST com quantidade=0 → 422."""
    token = _register_and_login(client)
    item_id = _setup_produto(client, token)
    response = client.post(f"/api/v1/estoque/{item_id}/entrada",
        json={"quantidade": 0}, headers=_auth_header(token))
    assert response.status_code == 422


def test_entrada_item_inexistente(client):
    """POST /estoque/{uuid-aleatorio}/entrada → 404."""
    token = _register_and_login(client)
    response = client.post(f"/api/v1/estoque/{uuid.uuid4()}/entrada",
        json={"quantidade": 10}, headers=_auth_header(token))
    assert response.status_code == 404


def test_listar_itens_estoque(client):
    """Criar 2 produtos → GET /estoque → 200 + lista."""
    token = _register_and_login(client)
    _setup_produto(client, token)
    _setup_produto(client, token)
    response = client.get("/api/v1/estoque", headers=_auth_header(token))
    assert response.status_code == 200
    assert len(response.json()) >= 2


def test_buscar_item_por_produto(client):
    """GET /estoque/produto/{produto_id} → 200."""
    token = _register_and_login(client)
    cat = client.post("/api/v1/categorias",
        json={"nome": f"BusCat-{uuid.uuid4().hex[:6]}"},
        headers=_auth_header(token)).json()
    prod = client.post("/api/v1/produtos",
        json={"sku": f"BUS-{uuid.uuid4().hex[:6]}", "nome": "Buscar", "preco": 10, "categoria_id": cat["id"]},
        headers=_auth_header(token)).json()
    response = client.get(f"/api/v1/estoque/produto/{prod['id']}", headers=_auth_header(token))
    assert response.status_code == 200
    assert response.json()["produto_id"] == prod["id"]


def test_historico_movimentacoes(client):
    """Fazer 3 entradas → GET movimentacoes → 3 registros."""
    token = _register_and_login(client)
    item_id = _setup_produto(client, token)
    for _ in range(3):
        client.post(f"/api/v1/estoque/{item_id}/entrada",
            json={"quantidade": 10}, headers=_auth_header(token))
    response = client.get(f"/api/v1/estoque/{item_id}/movimentacoes", headers=_auth_header(token))
    assert response.status_code == 200
    assert len(response.json()) == 3


# --- Saida ---

def test_registrar_saida(client):
    """Entrada 100 + Saida 30 → 201, saldo=70."""
    token = _register_and_login(client)
    item_id = _setup_produto(client, token)
    client.post(f"/api/v1/estoque/{item_id}/entrada",
        json={"quantidade": 100}, headers=_auth_header(token))
    response = client.post(f"/api/v1/estoque/{item_id}/saida",
        json={"quantidade": 30, "motivo": "Venda"}, headers=_auth_header(token))
    assert response.status_code == 201
    item = client.get(f"/api/v1/estoque/{item_id}", headers=_auth_header(token)).json()
    assert item["saldo"] == 70


def test_saida_estoque_insuficiente(client):
    """Entrada 10 + Saida 20 → 422."""
    token = _register_and_login(client)
    item_id = _setup_produto(client, token)
    client.post(f"/api/v1/estoque/{item_id}/entrada",
        json={"quantidade": 10}, headers=_auth_header(token))
    response = client.post(f"/api/v1/estoque/{item_id}/saida",
        json={"quantidade": 20}, headers=_auth_header(token))
    assert response.status_code == 422


def test_saida_zera_estoque(client):
    """Entrada 50 + Saida 50 → saldo=0."""
    token = _register_and_login(client)
    item_id = _setup_produto(client, token)
    client.post(f"/api/v1/estoque/{item_id}/entrada",
        json={"quantidade": 50}, headers=_auth_header(token))
    client.post(f"/api/v1/estoque/{item_id}/saida",
        json={"quantidade": 50}, headers=_auth_header(token))
    item = client.get(f"/api/v1/estoque/{item_id}", headers=_auth_header(token)).json()
    assert item["saldo"] == 0


def test_multiplas_movimentacoes(client):
    """Entrada 100, saida 30, saida 30 → saldo=40, 3 movimentacoes."""
    token = _register_and_login(client)
    item_id = _setup_produto(client, token)
    client.post(f"/api/v1/estoque/{item_id}/entrada",
        json={"quantidade": 100}, headers=_auth_header(token))
    client.post(f"/api/v1/estoque/{item_id}/saida",
        json={"quantidade": 30}, headers=_auth_header(token))
    client.post(f"/api/v1/estoque/{item_id}/saida",
        json={"quantidade": 30}, headers=_auth_header(token))
    item = client.get(f"/api/v1/estoque/{item_id}", headers=_auth_header(token)).json()
    assert item["saldo"] == 40
    movs = client.get(f"/api/v1/estoque/{item_id}/movimentacoes", headers=_auth_header(token)).json()
    assert len(movs) == 3
