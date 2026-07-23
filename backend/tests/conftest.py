"""
Fixtures compartilhadas dos testes do backend.

Responsabilidades:
- Fornecer um TestClient isolado por teste, com banco SQLite em memória.
- Fornecer um TestClient com banco em arquivo, para testes de concorrência real.
"""
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """Cria um TestClient com banco SQLite em memória, isolado deste teste.

    Returns:
        TestClient com o dependency override de `get_db` aplicado.
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
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
