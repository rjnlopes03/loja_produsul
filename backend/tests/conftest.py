"""
Fixtures compartilhadas dos testes do backend.

Responsabilidades:
- Fornecer um TestClient isolado por teste, com banco SQLite em memória.
- Fornecer um TestClient com banco em arquivo, para testes de concorrência real.
- Isolar o estado de autenticação (tokens/tentativas) entre testes, já
  que `app.auth` guarda esse estado em variáveis globais do processo.
"""
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.auth as auth_module
from app.auth import AUTH_PASSWORD, AUTH_USERNAME
from app.database import Base, get_db
from app.main import app


@pytest.fixture(autouse=True)
def _isolar_estado_auth() -> Iterator[None]:
    """Limpa tokens/tentativas de login entre testes.

    `app.auth` guarda esse estado em dicts no nível do módulo (memória
    do processo); sem isso, um teste que força tentativas de login
    malsucedidas vazaria o bloqueio por tentativas para os próximos.
    """
    auth_module._tokens_validos.clear()
    auth_module._tentativas_falhas.clear()
    yield
    auth_module._tokens_validos.clear()
    auth_module._tentativas_falhas.clear()


def _autenticar(test_client: TestClient) -> None:
    """Loga com as credenciais de teste e anexa o token como header padrão.

    Args:
        test_client: Cliente de teste já com o override de `get_db` aplicado.
    """
    token = test_client.post(
        "/auth/login", json={"usuario": AUTH_USERNAME, "senha": AUTH_PASSWORD}
    ).json()["token"]
    test_client.headers.update({"Authorization": f"Bearer {token}"})


@pytest.fixture()
def client() -> Iterator[TestClient]:
    """Cria um TestClient com banco SQLite em memória, isolado deste teste.

    Já vem autenticado (token válido anexado como header padrão).

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
    test_client = TestClient(app)
    _autenticar(test_client)
    yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def client_multithread(tmp_path: Path) -> Iterator[TestClient]:
    """TestClient com banco SQLite em arquivo e pool de conexões real.

    Diferente da fixture `client` (in-memory + StaticPool, uma única
    conexão), aqui cada thread recebe sua própria conexão ao mesmo
    arquivo — reproduzindo o cenário de concorrência real da produção
    (`sqlite:///./loja.db`), necessário para testar corridas de fato.

    Já vem autenticado (token válido anexado como header padrão).

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
    test_client = TestClient(app)
    _autenticar(test_client)
    yield test_client
    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
    engine.dispose()
