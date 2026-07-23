"""
Testes de concorrência no ajuste de estoque.

Responsabilidades:
- Garantir que compras concorrentes não vendem mais do que o estoque disponível.
"""
from collections.abc import Iterator
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client_multithread(tmp_path: Path) -> Iterator[TestClient]:
    """TestClient com banco SQLite em arquivo e pool de conexões real.

    Diferente da fixture `client` (in-memory + StaticPool, uma única
    conexão), aqui cada thread recebe sua própria conexão ao mesmo
    arquivo — reproduzindo o cenário de concorrência real da produção
    (`sqlite:///./loja.db`), necessário para testar corridas de fato.

    Returns:
        TestClient com o dependency override de `get_db` aplicado.
    """
    db_path = tmp_path / "teste.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()


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
