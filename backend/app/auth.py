import hashlib
import hmac
import os
import time
from typing import Optional

from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel

# Senha do administrador. Sem ela (uso local), o login fica desligado.
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")
VALIDADE_TOKEN_S = 7 * 24 * 3600

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    senha: str


def _assinar(texto: str) -> str:
    # A chave deriva da senha: trocar a senha invalida todas as sessões abertas.
    chave = hashlib.sha256(f"produsul:{ADMIN_PASSWORD}".encode()).digest()
    return hmac.new(chave, texto.encode(), hashlib.sha256).hexdigest()


def gerar_token() -> str:
    expira = str(int(time.time()) + VALIDADE_TOKEN_S)
    return f"{expira}.{_assinar(expira)}"


def token_valido(token: str) -> bool:
    expira, _, assinatura = token.partition(".")
    if not expira.isdigit():
        return False
    return hmac.compare_digest(assinatura, _assinar(expira)) and int(expira) > time.time()


def exigir_admin(authorization: Optional[str] = Header(default=None)):
    if not ADMIN_PASSWORD:
        return
    token = authorization.removeprefix("Bearer ").strip() if authorization else ""
    if not token_valido(token):
        raise HTTPException(status_code=401, detail="Sessão expirada. Entre novamente.")


@router.get("/status")
def status_login():
    return {"login_obrigatorio": bool(ADMIN_PASSWORD)}


@router.post("/login")
def login(dados: LoginRequest):
    if not ADMIN_PASSWORD:
        return {"token": ""}
    if not hmac.compare_digest(dados.senha.encode(), ADMIN_PASSWORD.encode()):
        # Atraso fixo para dificultar tentativas em massa de senha.
        time.sleep(1)
        raise HTTPException(status_code=401, detail="Senha incorreta")
    return {"token": gerar_token()}
