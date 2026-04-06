from uuid import uuid4

from fastapi.testclient import TestClient


def _get_token(client: TestClient) -> str:
    email = f"prod-{uuid4().hex[:8]}@test.com"
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


def test_criar_produto(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    sku = f"SKU-{uuid4().hex[:8]}"

    response = client.post(
        "/api/v1/produtos",
        json={
            "sku": sku,
            "nome": "Teclado Mecanico",
            "descricao": "Switches blue",
            "preco": 299.90,
            "categoria_id": cat["id"],
        },
        headers=_auth_header(token),
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert data["sku"] == sku
    assert data["nome"] == "Teclado Mecanico"
    assert float(data["preco"]) == 299.90
    assert data["categoria"]["id"] == cat["id"]
    assert data["categoria"]["nome"] == cat["nome"]
    assert data["ativo"] is True
    assert "criado_em" in data
    assert "atualizado_em" in data


def test_criar_produto_sku_duplicado(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    sku = f"SKU-{uuid4().hex[:8]}"
    payload = {
        "sku": sku,
        "nome": "Produto A",
        "preco": 100.00,
        "categoria_id": cat["id"],
    }

    client.post("/api/v1/produtos", json=payload, headers=_auth_header(token))
    response = client.post("/api/v1/produtos", json=payload, headers=_auth_header(token))
    assert response.status_code == 409
    assert response.json()["code"] == "PRODUTO_SKU_DUPLICADO"


def test_criar_produto_preco_invalido(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)

    response = client.post(
        "/api/v1/produtos",
        json={
            "sku": f"SKU-{uuid4().hex[:8]}",
            "nome": "Produto X",
            "preco": 0,
            "categoria_id": cat["id"],
        },
        headers=_auth_header(token),
    )
    assert response.status_code == 422


def test_criar_produto_categoria_inexistente(client: TestClient):
    token = _get_token(client)

    response = client.post(
        "/api/v1/produtos",
        json={
            "sku": f"SKU-{uuid4().hex[:8]}",
            "nome": "Produto Y",
            "preco": 50.00,
            "categoria_id": str(uuid4()),
        },
        headers=_auth_header(token),
    )
    assert response.status_code == 404
    assert response.json()["code"] == "CATEGORIA_NAO_ENCONTRADA"


def test_listar_produtos(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)

    for i in range(3):
        client.post(
            "/api/v1/produtos",
            json={
                "sku": f"LIST-{uuid4().hex[:8]}",
                "nome": f"Produto List {i}",
                "preco": 10.00 + i,
                "categoria_id": cat["id"],
            },
            headers=_auth_header(token),
        )

    response = client.get(
        f"/api/v1/produtos?categoria_id={cat['id']}",
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3


def test_listar_produtos_filtro_categoria(client: TestClient):
    token = _get_token(client)
    cat_a = _criar_categoria(client, token)
    cat_b = _criar_categoria(client, token)

    for i in range(2):
        client.post(
            "/api/v1/produtos",
            json={
                "sku": f"FILTA-{uuid4().hex[:8]}",
                "nome": f"Prod A{i}",
                "preco": 10.00,
                "categoria_id": cat_a["id"],
            },
            headers=_auth_header(token),
        )
    client.post(
        "/api/v1/produtos",
        json={
            "sku": f"FILTB-{uuid4().hex[:8]}",
            "nome": "Prod B0",
            "preco": 20.00,
            "categoria_id": cat_b["id"],
        },
        headers=_auth_header(token),
    )

    response = client.get(
        f"/api/v1/produtos?categoria_id={cat_a['id']}",
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2


def test_buscar_produto_por_id(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    sku = f"BUSCA-{uuid4().hex[:8]}"

    create_resp = client.post(
        "/api/v1/produtos",
        json={
            "sku": sku,
            "nome": "Produto Busca",
            "preco": 55.50,
            "categoria_id": cat["id"],
        },
        headers=_auth_header(token),
    )
    produto_id = create_resp.json()["id"]

    response = client.get(
        f"/api/v1/produtos/{produto_id}",
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == produto_id
    assert data["sku"] == sku


def test_atualizar_produto(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)
    sku = f"UPDT-{uuid4().hex[:8]}"

    create_resp = client.post(
        "/api/v1/produtos",
        json={
            "sku": sku,
            "nome": "Produto Original",
            "preco": 100.00,
            "categoria_id": cat["id"],
        },
        headers=_auth_header(token),
    )
    data_criado = create_resp.json()
    produto_id = data_criado["id"]

    response = client.put(
        f"/api/v1/produtos/{produto_id}",
        json={"nome": "Produto Atualizado", "preco": 150.00},
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["nome"] == "Produto Atualizado"
    assert float(data["preco"]) == 150.00
    assert data["sku"] == sku
    assert data["atualizado_em"] != data_criado["atualizado_em"]


def test_desativar_produto(client: TestClient):
    token = _get_token(client)
    cat = _criar_categoria(client, token)

    create_resp = client.post(
        "/api/v1/produtos",
        json={
            "sku": f"DESAT-{uuid4().hex[:8]}",
            "nome": "Produto Ativo",
            "preco": 30.00,
            "categoria_id": cat["id"],
        },
        headers=_auth_header(token),
    )
    produto_id = create_resp.json()["id"]

    response = client.patch(
        f"/api/v1/produtos/{produto_id}/desativar",
        headers=_auth_header(token),
    )
    assert response.status_code == 200
    data = response.json()
    assert data["ativo"] is False
