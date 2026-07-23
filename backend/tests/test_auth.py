"""
Testes de autenticação.

Responsabilidades:
- Cobrir login (sucesso/falha) e o bloqueio de rotas protegidas
  sem um token válido.
- Cobrir logout (revogação de token) e o limite de tentativas de login.
"""
import time

from fastapi.testclient import TestClient

import app.auth as auth_module
from app.auth import AUTH_PASSWORD, AUTH_USERNAME, LIMITE_TENTATIVAS


def test_login_com_credenciais_corretas_retorna_token(client: TestClient) -> None:
    resposta = client.post("/auth/login", json={"usuario": AUTH_USERNAME, "senha": AUTH_PASSWORD})

    assert resposta.status_code == 200
    assert resposta.json()["token"]


def test_login_com_credenciais_erradas_retorna_401(client: TestClient) -> None:
    resposta = client.post("/auth/login", json={"usuario": AUTH_USERNAME, "senha": "errada"})

    assert resposta.status_code == 401


def test_rota_protegida_sem_token_retorna_401(client: TestClient) -> None:
    client.headers.pop("Authorization", None)

    resposta = client.get("/produtos/")

    assert resposta.status_code == 401


def test_rota_protegida_com_token_invalido_retorna_401(client: TestClient) -> None:
    client.headers.update({"Authorization": "Bearer token-invalido"})

    resposta = client.get("/produtos/")

    assert resposta.status_code == 401


def test_rota_protegida_com_token_valido_funciona(client: TestClient) -> None:
    resposta = client.get("/produtos/")

    assert resposta.status_code == 200


def test_logout_revoga_token(client: TestClient) -> None:
    resposta_logout = client.post("/auth/logout")
    assert resposta_logout.status_code == 204

    resposta = client.get("/produtos/")

    assert resposta.status_code == 401


def test_login_apos_muitas_tentativas_falhas_retorna_429(client: TestClient) -> None:
    for _ in range(LIMITE_TENTATIVAS):
        client.post("/auth/login", json={"usuario": AUTH_USERNAME, "senha": "errada"})

    resposta = client.post("/auth/login", json={"usuario": AUTH_USERNAME, "senha": AUTH_PASSWORD})

    assert resposta.status_code == 429


def test_login_com_tentativas_falhas_antigas_nao_conta_no_limite(client: TestClient) -> None:
    for _ in range(LIMITE_TENTATIVAS):
        client.post("/auth/login", json={"usuario": AUTH_USERNAME, "senha": "errada"})

    # simula que as tentativas ficaram fora da janela de tempo
    auth_module._tentativas_falhas[AUTH_USERNAME] = [
        t - auth_module.JANELA_TENTATIVAS_SEGUNDOS - 1
        for t in auth_module._tentativas_falhas[AUTH_USERNAME]
    ]

    resposta = client.post("/auth/login", json={"usuario": AUTH_USERNAME, "senha": AUTH_PASSWORD})

    assert resposta.status_code == 200


def test_token_expirado_retorna_401(client: TestClient) -> None:
    token = client.headers["Authorization"].removeprefix("Bearer ").strip()
    auth_module._tokens_validos[token] = time.time() - auth_module.TOKEN_TTL_SEGUNDOS - 1

    resposta = client.get("/produtos/")

    assert resposta.status_code == 401
