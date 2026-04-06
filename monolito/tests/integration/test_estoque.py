from uuid import uuid4

from fastapi.testclient import TestClient


def _get_token(client: TestClient) -> str:
    email = f"est-{uuid4().hex[:8]}@test.com"
    client.post(
        "/api/v1/auth/registrar",
        json={"nome": "Admin", "email": email, "senha": "minimo8chars"},
    )
    resp = client.post(
        "/api/v1/auth/login",
        json={"email": email, "senha": "minimo8chars"},
    )
    return resp.json()["access_token"]


def _auth_header(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _criar_categoria(client: TestClient, token: str) -> dict:
    nome = f"Cat-{uuid4().hex[:8]}"
    resp = client.post(
        "/api/v1/categorias",
        json={"nome": nome, "descricao": "Categoria teste"},
        headers=_auth_header(token),
    )
    return resp.json()


def _criar_produto(client: TestClient, token: str, categoria_id: str) -> dict:
    sku = f"SKU-{uuid4().hex[:8]}"
    resp = client.post(
        "/api/v1/produtos",
        json={
            "sku": sku,
            "nome": "Produto Estoque",
            "preco": 50.00,
            "categoria_id": categoria_id,
        },
        headers=_auth_header(token),
    )
    return resp.json()


def _get_item_by_produto(client: TestClient, token: str, produto_id: str) -> dict:
    resp = client.get(
        f"/api/v1/estoque/produto/{produto_id}",
        headers=_auth_header(token),
    )
    return resp.json()


def test_registrar_entrada(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    produto = _criar_produto(client, token, cat["id"])
    item = _get_item_by_produto(client, token, produto["id"])

    response = client.post(
        f"/api/v1/estoque/{item['id']}/entrada",
        json={"quantidade": 100, "lote": "NF-001", "motivo": "Recebimento"},
        headers=_auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tipo"] == "ENTRADA"
    assert data["quantidade"] == 100
    assert data["lote"] == "NF-001"
    assert data["motivo"] == "Recebimento"
    assert data["item_estoque_id"] == item["id"]


def test_saldo_apos_entrada(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    produto = _criar_produto(client, token, cat["id"])
    item = _get_item_by_produto(client, token, produto["id"])

    client.post(
        f"/api/v1/estoque/{item['id']}/entrada",
        json={"quantidade": 100},
        headers=_auth_header(token),
    )
    resp = client.get(
        f"/api/v1/estoque/{item['id']}",
        headers=_auth_header(token),
    )
    assert resp.json()["saldo"] == 100

    client.post(
        f"/api/v1/estoque/{item['id']}/entrada",
        json={"quantidade": 50},
        headers=_auth_header(token),
    )
    resp = client.get(
        f"/api/v1/estoque/{item['id']}",
        headers=_auth_header(token),
    )
    assert resp.json()["saldo"] == 150


def test_entrada_quantidade_invalida(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    produto = _criar_produto(client, token, cat["id"])
    item = _get_item_by_produto(client, token, produto["id"])

    response = client.post(
        f"/api/v1/estoque/{item['id']}/entrada",
        json={"quantidade": 0},
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_entrada_item_inexistente(client: TestClient):
    token = _get_token(client)

    response = client.post(
        f"/api/v1/estoque/{uuid4()}/entrada",
        json={"quantidade": 10},
        headers=_auth_header(token),
    )
    assert response.status_code == 404
    assert response.json()["code"] == "ESTOQUE_ITEM_NAO_ENCONTRADO"


def test_listar_itens_estoque(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    _criar_produto(client, token, cat["id"])
    _criar_produto(client, token, cat["id"])

    response = client.get(
        "/api/v1/estoque",
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 2


def test_buscar_item_por_produto(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    produto = _criar_produto(client, token, cat["id"])

    response = client.get(
        f"/api/v1/estoque/produto/{produto['id']}",
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["produto_id"] == produto["id"]
    assert data["sku"] == produto["sku"]
    assert data["saldo"] == 0


def test_registrar_saida(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    produto = _criar_produto(client, token, cat["id"])
    item = _get_item_by_produto(client, token, produto["id"])

    # Entrada de 100
    client.post(
        f"/api/v1/estoque/{item['id']}/entrada",
        json={"quantidade": 100},
        headers=_auth_header(token),
    )

    # Saida de 30
    response = client.post(
        f"/api/v1/estoque/{item['id']}/saida",
        json={"quantidade": 30, "motivo": "Venda"},
        headers=_auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert data["tipo"] == "SAIDA"
    assert data["quantidade"] == 30
    assert data["motivo"] == "Venda"

    # Saldo deve ser 70
    resp = client.get(
        f"/api/v1/estoque/{item['id']}",
        headers=_auth_header(token),
    )
    assert resp.json()["saldo"] == 70


def test_saida_estoque_insuficiente(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    produto = _criar_produto(client, token, cat["id"])
    item = _get_item_by_produto(client, token, produto["id"])

    # Entrada de 10
    client.post(
        f"/api/v1/estoque/{item['id']}/entrada",
        json={"quantidade": 10},
        headers=_auth_header(token),
    )

    # Saida de 20 — insuficiente
    response = client.post(
        f"/api/v1/estoque/{item['id']}/saida",
        json={"quantidade": 20},
        headers=_auth_header(token),
    )
    assert response.status_code == 422
    assert response.json()["code"] == "ESTOQUE_INSUFICIENTE"

    # Saldo nao alterou
    resp = client.get(
        f"/api/v1/estoque/{item['id']}",
        headers=_auth_header(token),
    )
    assert resp.json()["saldo"] == 10


def test_saida_zera_estoque(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    produto = _criar_produto(client, token, cat["id"])
    item = _get_item_by_produto(client, token, produto["id"])

    # Entrada de 50
    client.post(
        f"/api/v1/estoque/{item['id']}/entrada",
        json={"quantidade": 50},
        headers=_auth_header(token),
    )

    # Saida de 50 — zera
    response = client.post(
        f"/api/v1/estoque/{item['id']}/saida",
        json={"quantidade": 50},
        headers=_auth_header(token),
    )
    assert response.status_code == 201

    resp = client.get(
        f"/api/v1/estoque/{item['id']}",
        headers=_auth_header(token),
    )
    assert resp.json()["saldo"] == 0


def test_multiplas_movimentacoes(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    produto = _criar_produto(client, token, cat["id"])
    item = _get_item_by_produto(client, token, produto["id"])

    # Entrada 100
    client.post(
        f"/api/v1/estoque/{item['id']}/entrada",
        json={"quantidade": 100},
        headers=_auth_header(token),
    )

    # Saida 30, Saida 30
    client.post(
        f"/api/v1/estoque/{item['id']}/saida",
        json={"quantidade": 30},
        headers=_auth_header(token),
    )
    client.post(
        f"/api/v1/estoque/{item['id']}/saida",
        json={"quantidade": 30},
        headers=_auth_header(token),
    )

    # Saldo = 40
    resp = client.get(
        f"/api/v1/estoque/{item['id']}",
        headers=_auth_header(token),
    )
    assert resp.json()["saldo"] == 40

    # 3 movimentacoes (1 entrada + 2 saidas)
    resp = client.get(
        f"/api/v1/estoque/{item['id']}/movimentacoes",
        headers=_auth_header(token),
    )
    assert len(resp.json()) == 3


def test_historico_movimentacoes(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    produto = _criar_produto(client, token, cat["id"])
    item = _get_item_by_produto(client, token, produto["id"])

    for i in range(3):
        client.post(
            f"/api/v1/estoque/{item['id']}/entrada",
            json={"quantidade": 10 * (i + 1)},
            headers=_auth_header(token),
        )

    response = client.get(
        f"/api/v1/estoque/{item['id']}/movimentacoes",
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
