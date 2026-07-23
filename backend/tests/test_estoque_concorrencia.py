"""
Testes de concorrência no ajuste de estoque.

Responsabilidades:
- Garantir que compras concorrentes não vendem mais do que o estoque disponível.
"""
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient


def test_compras_concorrentes_nao_vendem_alem_do_estoque(client_multithread: TestClient) -> None:
    client = client_multithread
    marca_id = client.post("/marcas/", json={"nome": "Golden"}).json()["id"]
    cliente_id = client.post("/clientes/", json={"nome": "Fulano"}).json()["id"]
    produto = client.post(
        "/produtos/",
        json={
            "nome": "Ração Teste",
            "marca_id": marca_id,
            "especie": "cachorro",
            "fase_vida": "adulto",
            "peso_kg": 10.0,
            "preco": 10.0,
            "quantidade_estoque": 7,
        },
    ).json()
    produto_id = produto["id"]

    def comprar(_: int) -> int:
        resposta = client.post(
            f"/clientes/{cliente_id}/compras",
            json={"produto_id": produto_id, "quantidade": 1},
        )
        return resposta.status_code

    with ThreadPoolExecutor(max_workers=8) as executor:
        status_codes = list(executor.map(comprar, range(8)))

    assert status_codes.count(201) == 7
    assert status_codes.count(400) == 1

    produto_final = client.get(f"/produtos/{produto_id}").json()
    assert produto_final["quantidade_estoque"] == 0
