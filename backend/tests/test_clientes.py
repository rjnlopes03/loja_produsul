"""
Testes da rota de clientes.

Responsabilidades:
- Garantir que o resumo do cliente reutiliza a mesma função de cálculo
  de saldo devedor usada na listagem, evitando duas fontes de verdade.
- Cobrir o bloqueio de exclusão de cliente com compras/pagamentos.
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
