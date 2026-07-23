"""
Testes da rota de marcas.

Responsabilidades:
- Cobrir a criação concorrente de marcas com o mesmo nome.
"""
from concurrent.futures import ThreadPoolExecutor

from fastapi.testclient import TestClient


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
