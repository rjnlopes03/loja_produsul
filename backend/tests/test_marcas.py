"""
Testes da rota de marcas.

Responsabilidades:
- Cobrir a criação concorrente de marcas com o mesmo nome.
- Cobrir o bloqueio de exclusão de marca referenciada por um produto.
"""
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient


def test_excluir_marca_com_produto_retorna_400(client: TestClient) -> None:
    marca_id = client.post("/marcas/", json={"nome": "Golden"}).json()["id"]
    client.post(
        "/produtos/",
        json={
            "nome": "Ração Teste",
            "marca_id": marca_id,
            "especie": "cachorro",
            "fase_vida": "adulto",
            "peso_kg": 10.0,
            "preco": 99.9,
            "quantidade_estoque": 5,
        },
    )

    resposta = client.delete(f"/marcas/{marca_id}")

    assert resposta.status_code == 400
    assert "produtos" in resposta.json()["detail"].lower()


def test_criar_marcas_concorrentes_com_mesmo_nome_nao_quebra_com_500(
    client_multithread: TestClient,
) -> None:
    def criar(_: int) -> int:
        try:
            resposta = client_multithread.post("/marcas/", json={"nome": "Golden"})
            return resposta.status_code
        except Exception:
            # TestClient propaga exceções não tratadas do servidor (ex.: um
            # IntegrityError não capturado) em vez de devolver um 500 comum.
            return 500

    with ThreadPoolExecutor(max_workers=5) as executor:
        status_codes = list(executor.map(criar, range(5)))

    assert status_codes.count(201) == 1
    assert status_codes.count(400) == 4
    assert 500 not in status_codes
