"""Testes da feature Alerta de Estoque Baixo — Monolito DDD.
Spec: docs/features/spec-alerta-estoque-baixo.md"""
from uuid import uuid4

from fastapi.testclient import TestClient


def _get_token(client: TestClient) -> str:
    email = f"alerta-{uuid4().hex[:8]}@test.com"
    client.post("/api/v1/auth/registrar", json={"nome": "Admin", "email": email, "senha": "minimo8chars"})
    resp = client.post("/api/v1/auth/login", json={"email": email, "senha": "minimo8chars"})
    return resp.json()["access_token"]


def _auth(token: str) -> dict:
    return {"Authorization": f"Bearer {token}"}


def _setup_item(client: TestClient, token: str) -> str:
    """Cria categoria + produto + retorna item_estoque_id."""
    cat = client.post("/api/v1/categorias", json={"nome": f"AC-{uuid4().hex[:6]}"}, headers=_auth(token)).json()
    prod = client.post("/api/v1/produtos", json={
        "sku": f"AL-{uuid4().hex[:6]}", "nome": "ProdAlerta", "preco": 10, "categoria_id": cat["id"],
    }, headers=_auth(token)).json()
    item = client.get(f"/api/v1/estoque/produto/{prod['id']}", headers=_auth(token)).json()
    return item["id"]


def test_configurar_alerta(client: TestClient):
    """PATCH configurar-alerta com estoque_minimo=10 → 200."""
    token = _get_token(client)
    item_id = _setup_item(client, token)
    resp = client.patch(
        f"/api/v1/estoque/{item_id}/configurar-alerta",
        json={"estoque_minimo": 10},
        headers=_auth(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["estoque_minimo"] == 10


def test_alerta_criado_quando_saldo_abaixo_minimo(client: TestClient):
    """Config min=10, entrada 15, saida 10 → saldo=5, 1 alerta."""
    token = _get_token(client)
    item_id = _setup_item(client, token)
    client.patch(f"/api/v1/estoque/{item_id}/configurar-alerta", json={"estoque_minimo": 10}, headers=_auth(token))
    client.post(f"/api/v1/estoque/{item_id}/entrada", json={"quantidade": 15}, headers=_auth(token))
    client.post(f"/api/v1/estoque/{item_id}/saida", json={"quantidade": 10}, headers=_auth(token))

    resp = client.get(f"/api/v1/estoque/{item_id}/alertas", headers=_auth(token))
    assert resp.status_code == 200
    alertas = resp.json()
    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "ESTOQUE_BAIXO"
    assert alertas[0]["saldo_atual"] == 5
    assert alertas[0]["estoque_minimo"] == 10


def test_sem_alerta_quando_saldo_acima_minimo(client: TestClient):
    """Config min=5, entrada 20, saida 10 → saldo=10, 0 alertas."""
    token = _get_token(client)
    item_id = _setup_item(client, token)
    client.patch(f"/api/v1/estoque/{item_id}/configurar-alerta", json={"estoque_minimo": 5}, headers=_auth(token))
    client.post(f"/api/v1/estoque/{item_id}/entrada", json={"quantidade": 20}, headers=_auth(token))
    client.post(f"/api/v1/estoque/{item_id}/saida", json={"quantidade": 10}, headers=_auth(token))

    resp = client.get(f"/api/v1/estoque/{item_id}/alertas", headers=_auth(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 0


def test_listar_alertas_multiplos(client: TestClient):
    """Config min=10, entrada 20, saida 8, saida 8 → 2 alertas."""
    token = _get_token(client)
    item_id = _setup_item(client, token)
    client.patch(f"/api/v1/estoque/{item_id}/configurar-alerta", json={"estoque_minimo": 10}, headers=_auth(token))
    client.post(f"/api/v1/estoque/{item_id}/entrada", json={"quantidade": 20}, headers=_auth(token))

    # saida 8: saldo = 12 → acima de 10, sem alerta
    client.post(f"/api/v1/estoque/{item_id}/saida", json={"quantidade": 8}, headers=_auth(token))
    # saida 8: saldo = 4 → abaixo de 10, alerta
    client.post(f"/api/v1/estoque/{item_id}/saida", json={"quantidade": 8}, headers=_auth(token))

    resp = client.get(f"/api/v1/estoque/{item_id}/alertas", headers=_auth(token))
    alertas = resp.json()
    assert len(alertas) == 1  # so a segunda saida gera alerta (saldo=4 < 10)
    assert alertas[0]["saldo_atual"] == 4
