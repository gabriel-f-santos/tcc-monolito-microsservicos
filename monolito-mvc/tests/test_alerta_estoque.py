"""Testes da feature Alerta de Estoque Baixo — Monolito MVC.
Spec: docs/features/spec-alerta-estoque-baixo.md"""
import uuid
from tests.conftest import _register_and_login, _auth_header


def _setup_item(client, token):
    """Cria categoria + produto + retorna item_estoque_id."""
    cat = client.post("/api/v1/categorias",
        json={"nome": f"AC-{uuid.uuid4().hex[:6]}"},
        headers=_auth_header(token),
    ).json()
    prod = client.post("/api/v1/produtos",
        json={"sku": f"AL-{uuid.uuid4().hex[:6]}", "nome": "ProdAlerta", "preco": 10, "categoria_id": cat["id"]},
        headers=_auth_header(token),
    ).json()
    item = client.get(f"/api/v1/estoque/produto/{prod['id']}", headers=_auth_header(token)).json()
    return item["id"]


def test_configurar_alerta(client):
    """PATCH configurar-alerta com estoque_minimo=10 → 200."""
    token = _register_and_login(client)
    item_id = _setup_item(client, token)
    resp = client.patch(
        f"/api/v1/estoque/{item_id}/configurar-alerta",
        json={"estoque_minimo": 10},
        headers=_auth_header(token),
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["estoque_minimo"] == 10


def test_alerta_criado_quando_saldo_abaixo_minimo(client):
    """Config min=10, entrada 15, saida 10 → saldo=5, 1 alerta."""
    token = _register_and_login(client)
    item_id = _setup_item(client, token)
    client.patch(f"/api/v1/estoque/{item_id}/configurar-alerta", json={"estoque_minimo": 10}, headers=_auth_header(token))
    client.post(f"/api/v1/estoque/{item_id}/entrada", json={"quantidade": 15}, headers=_auth_header(token))
    client.post(f"/api/v1/estoque/{item_id}/saida", json={"quantidade": 10}, headers=_auth_header(token))

    resp = client.get(f"/api/v1/estoque/{item_id}/alertas", headers=_auth_header(token))
    assert resp.status_code == 200
    alertas = resp.json()
    assert len(alertas) == 1
    assert alertas[0]["tipo"] == "ESTOQUE_BAIXO"
    assert alertas[0]["saldo_atual"] == 5
    assert alertas[0]["estoque_minimo"] == 10


def test_sem_alerta_quando_saldo_acima_minimo(client):
    """Config min=5, entrada 20, saida 10 → saldo=10, 0 alertas."""
    token = _register_and_login(client)
    item_id = _setup_item(client, token)
    client.patch(f"/api/v1/estoque/{item_id}/configurar-alerta", json={"estoque_minimo": 5}, headers=_auth_header(token))
    client.post(f"/api/v1/estoque/{item_id}/entrada", json={"quantidade": 20}, headers=_auth_header(token))
    client.post(f"/api/v1/estoque/{item_id}/saida", json={"quantidade": 10}, headers=_auth_header(token))

    resp = client.get(f"/api/v1/estoque/{item_id}/alertas", headers=_auth_header(token))
    assert resp.status_code == 200
    assert len(resp.json()) == 0


def test_listar_alertas_multiplos(client):
    """Config min=10, entrada 20, saida 8, saida 8 → 1 alerta (so a segunda)."""
    token = _register_and_login(client)
    item_id = _setup_item(client, token)
    client.patch(f"/api/v1/estoque/{item_id}/configurar-alerta", json={"estoque_minimo": 10}, headers=_auth_header(token))
    client.post(f"/api/v1/estoque/{item_id}/entrada", json={"quantidade": 20}, headers=_auth_header(token))
    client.post(f"/api/v1/estoque/{item_id}/saida", json={"quantidade": 8}, headers=_auth_header(token))
    client.post(f"/api/v1/estoque/{item_id}/saida", json={"quantidade": 8}, headers=_auth_header(token))

    resp = client.get(f"/api/v1/estoque/{item_id}/alertas", headers=_auth_header(token))
    alertas = resp.json()
    assert len(alertas) == 1
    assert alertas[0]["saldo_atual"] == 4
