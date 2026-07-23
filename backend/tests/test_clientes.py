"""
Testes da rota de clientes.

Responsabilidades:
- Garantir que o resumo do cliente reutiliza a mesma função de cálculo
  de saldo devedor usada na listagem, evitando duas fontes de verdade.
- Cobrir o bloqueio de exclusão de cliente com compras/pagamentos.
- Cobrir o estorno de compras e seu efeito no saldo e no estoque.
"""
from unittest.mock import ANY, patch

from fastapi.testclient import TestClient


def _criar_cliente(client: TestClient, nome: str = "Fulano") -> int:
    """Cria um cliente via API e retorna seu id.

    Args:
        client: Cliente de teste da API.
        nome: Nome do cliente a ser criado.

    Returns:
        Id do cliente criado.
    """
    resposta = client.post("/clientes/", json={"nome": nome})
    return resposta.json()["id"]


def _criar_produto(client: TestClient, **overrides: object) -> dict:
    """Cria uma marca e um produto via API e retorna o produto completo."""
    marca_id = client.post("/marcas/", json={"nome": "Golden"}).json()["id"]
    payload = {
        "nome": "Ração Teste",
        "marca_id": marca_id,
        "especie": "cachorro",
        "fase_vida": "adulto",
        "peso_kg": 10.0,
        "preco": 50.0,
        "quantidade_estoque": 10,
    }
    payload.update(overrides)
    return client.post("/produtos/", json=payload).json()


def test_excluir_cliente_com_pagamento_retorna_400(client: TestClient) -> None:
    cliente_id = _criar_cliente(client)
    client.post(f"/clientes/{cliente_id}/pagamentos", json={"valor": 10.0})

    resposta = client.delete(f"/clientes/{cliente_id}")

    assert resposta.status_code == 400
    assert "compras ou pagamentos" in resposta.json()["detail"].lower()


def test_resumo_cliente_reutiliza_saldo_devedor_compartilhado(client: TestClient) -> None:
    cliente_id = _criar_cliente(client)

    with patch("app.routers.clientes._saldo_devedor", return_value=12345.0) as mock_saldo:
        resposta = client.get(f"/clientes/{cliente_id}/resumo")

    assert resposta.status_code == 200
    assert resposta.json()["saldo_devedor"] == 12345.0
    mock_saldo.assert_called_once_with(ANY, cliente_id)


def test_estornar_compra_devolve_estoque_e_zera_saldo(client: TestClient) -> None:
    produto = _criar_produto(client, quantidade_estoque=10, preco=50.0)
    cliente_id = _criar_cliente(client)
    compra = client.post(
        f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 3}
    ).json()

    resposta = client.post(f"/clientes/{cliente_id}/compras/{compra['id']}/estornar")

    assert resposta.status_code == 200
    assert resposta.json()["estornado_em"] is not None

    produto_final = client.get(f"/produtos/{produto['id']}").json()
    assert produto_final["quantidade_estoque"] == 10

    cliente_final = next(
        c for c in client.get("/clientes/").json() if c["id"] == cliente_id
    )
    assert cliente_final["saldo_devedor"] == 0


def test_estornar_compra_ja_estornada_retorna_400(client: TestClient) -> None:
    produto = _criar_produto(client)
    cliente_id = _criar_cliente(client)
    compra = client.post(
        f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 1}
    ).json()
    client.post(f"/clientes/{cliente_id}/compras/{compra['id']}/estornar")

    resposta = client.post(f"/clientes/{cliente_id}/compras/{compra['id']}/estornar")

    assert resposta.status_code == 400


def test_resumo_cliente_mantem_compra_estornada_visivel_mas_fora_do_total(
    client: TestClient,
) -> None:
    produto = _criar_produto(client, preco=50.0)
    cliente_id = _criar_cliente(client)
    compra = client.post(
        f"/clientes/{cliente_id}/compras", json={"produto_id": produto["id"], "quantidade": 2}
    ).json()
    client.post(f"/clientes/{cliente_id}/compras/{compra['id']}/estornar")

    resumo = client.get(f"/clientes/{cliente_id}/resumo").json()

    assert len(resumo["compras"]) == 1
    assert resumo["compras"][0]["estornado_em"] is not None
    assert resumo["total_compras"] == 0
    assert resumo["saldo_devedor"] == 0
