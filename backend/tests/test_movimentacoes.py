"""
Testes da rota de movimentações.

Responsabilidades:
- Cobrir o estorno de movimentações (reversão de entrada/saída).
"""
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient


def _criar_marca(client: TestClient, nome: str = "Golden") -> int:
    """Cria uma marca via API e retorna seu id."""
    return client.post("/marcas/", json={"nome": nome}).json()["id"]


def _criar_produto(client: TestClient, marca_id: int, **overrides: object) -> dict:
    """Cria um produto via API e retorna o objeto completo."""
    payload = {
        "nome": "Ração Teste",
        "marca_id": marca_id,
        "especie": "cachorro",
        "fase_vida": "adulto",
        "peso_kg": 10.0,
        "preco": 99.9,
        "quantidade_estoque": 5,
    }
    payload.update(overrides)
    return client.post("/produtos/", json=payload).json()


def test_estornar_movimentacao_de_entrada_reverte_estoque(client: TestClient) -> None:
    marca_id = _criar_marca(client)
    produto = _criar_produto(client, marca_id, quantidade_estoque=5)
    mov = client.post(
        "/movimentacoes/", json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 10}
    ).json()

    resposta = client.post(f"/movimentacoes/{mov['id']}/estornar")

    assert resposta.status_code == 201
    estorno = resposta.json()
    assert estorno["tipo"] == "saida"
    assert estorno["quantidade"] == 10
    assert estorno["estorno_de_id"] == mov["id"]

    produto_final = client.get(f"/produtos/{produto['id']}").json()
    assert produto_final["quantidade_estoque"] == 5


def test_estornar_movimentacao_ja_estornada_retorna_400(client: TestClient) -> None:
    marca_id = _criar_marca(client)
    produto = _criar_produto(client, marca_id, quantidade_estoque=5)
    mov = client.post(
        "/movimentacoes/", json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 3}
    ).json()
    client.post(f"/movimentacoes/{mov['id']}/estornar")

    resposta = client.post(f"/movimentacoes/{mov['id']}/estornar")

    assert resposta.status_code == 400


def test_estornar_movimentacao_de_saida_sem_estoque_suficiente_retorna_400(
    client: TestClient,
) -> None:
    marca_id = _criar_marca(client)
    produto = _criar_produto(client, marca_id, quantidade_estoque=10)
    mov = client.post(
        "/movimentacoes/", json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 5}
    ).json()
    # consome o estoque recem-entrado antes de tentar estornar a entrada
    client.post(
        "/movimentacoes/", json={"produto_id": produto["id"], "tipo": "saida", "quantidade": 14}
    )

    resposta = client.post(f"/movimentacoes/{mov['id']}/estornar")

    assert resposta.status_code == 400


def test_estornos_concorrentes_da_mesma_movimentacao_so_aplicam_uma_vez(
    client_multithread: TestClient,
) -> None:
    marca_id = client_multithread.post("/marcas/", json={"nome": "Golden"}).json()["id"]
    produto = client_multithread.post(
        "/produtos/",
        json={
            "nome": "Ração Teste",
            "marca_id": marca_id,
            "especie": "cachorro",
            "fase_vida": "adulto",
            "peso_kg": 10.0,
            "preco": 50.0,
            "quantidade_estoque": 5,
        },
    ).json()
    mov = client_multithread.post(
        "/movimentacoes/", json={"produto_id": produto["id"], "tipo": "entrada", "quantidade": 10}
    ).json()

    def estornar(_: int) -> int:
        resposta = client_multithread.post(f"/movimentacoes/{mov['id']}/estornar")
        return resposta.status_code

    with ThreadPoolExecutor(max_workers=8) as executor:
        status_codes = list(executor.map(estornar, range(8)))

    assert status_codes.count(201) == 1
    assert status_codes.count(400) == 7

    produto_final = client_multithread.get(f"/produtos/{produto['id']}").json()
    assert produto_final["quantidade_estoque"] == 5
