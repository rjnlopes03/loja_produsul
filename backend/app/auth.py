"""
Autenticação simples da API via token opaco em memória.

Responsabilidades:
- Validar usuário/senha configurados por variável de ambiente.
- Emitir, validar e revogar tokens de sessão, guardados em memória do
  processo (sem tabela de usuários nem multiusuário — fora do escopo atual).
- Expirar tokens antigos e limitar tentativas de login para dificultar
  força bruta sobre credenciais fracas/padrão.
"""

import os
import secrets
import time

from fastapi import Header, HTTPException

AUTH_USERNAME = os.environ.get("AUTH_USERNAME", "admin")
AUTH_PASSWORD = os.environ.get("AUTH_PASSWORD", "123")

TOKEN_TTL_SEGUNDOS = 12 * 60 * 60
LIMITE_TENTATIVAS = 5
JANELA_TENTATIVAS_SEGUNDOS = 15 * 60

_tokens_validos: dict[str, float] = {}
_tentativas_falhas: dict[str, list[float]] = {}


def _podar_tokens_expirados() -> None:
    agora = time.time()
    expirados = [
        token
        for token, criado_em in _tokens_validos.items()
        if agora - criado_em > TOKEN_TTL_SEGUNDOS
    ]
    for token in expirados:
        del _tokens_validos[token]


def _tentativas_recentes(usuario: str) -> list[float]:
    agora = time.time()
    tentativas = _tentativas_falhas.get(usuario, [])
    return [t for t in tentativas if agora - t <= JANELA_TENTATIVAS_SEGUNDOS]


def _extrair_token(authorization: str) -> str:
    return authorization.removeprefix("Bearer ").strip()


def autenticar(usuario: str, senha: str) -> str:
    """Valida usuário/senha e emite um novo token de sessão.

    Bloqueia com 429 se o usuário acumulou tentativas malsucedidas
    demais numa janela curta de tempo, para dificultar força bruta.

    Args:
        usuario: Nome de usuário informado.
        senha: Senha informada.

    Returns:
        Token opaco válido para autenticar requisições futuras.

    Raises:
        HTTPException: 429 se houve tentativas demais recentemente;
            401 se usuário ou senha não conferem.
    """
    tentativas_recentes = _tentativas_recentes(usuario)
    if len(tentativas_recentes) >= LIMITE_TENTATIVAS:
        raise HTTPException(
            status_code=429,
            detail="Muitas tentativas de login. Aguarde e tente novamente.",
        )

    usuario_ok = secrets.compare_digest(usuario, AUTH_USERNAME)
    senha_ok = secrets.compare_digest(senha, AUTH_PASSWORD)
    if not (usuario_ok and senha_ok):
        tentativas_recentes.append(time.time())
        _tentativas_falhas[usuario] = tentativas_recentes
        raise HTTPException(status_code=401, detail="Usuário ou senha inválidos")

    _tentativas_falhas.pop(usuario, None)
    _podar_tokens_expirados()
    token = secrets.token_urlsafe(32)
    _tokens_validos[token] = time.time()
    return token


def exigir_autenticacao(authorization: str = Header(default="")) -> None:
    """Dependency que bloqueia a requisição se o token for ausente ou inválido.

    Args:
        authorization: Cabeçalho `Authorization: Bearer <token>`.

    Raises:
        HTTPException: 401 se o token estiver ausente, expirado ou não for válido.
    """
    _podar_tokens_expirados()
    token = _extrair_token(authorization)
    if not token or token not in _tokens_validos:
        raise HTTPException(status_code=401, detail="Não autenticado")


def revogar(authorization: str = Header(default="")) -> None:
    """Remove o token atual do conjunto de tokens válidos (logout).

    Args:
        authorization: Cabeçalho `Authorization: Bearer <token>`.
    """
    _tokens_validos.pop(_extrair_token(authorization), None)
