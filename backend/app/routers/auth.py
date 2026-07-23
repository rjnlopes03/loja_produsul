from fastapi import APIRouter, Depends, Header

from .. import schemas
from ..auth import autenticar, exigir_autenticacao, revogar

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=schemas.LoginResponse)
def login(dados: schemas.LoginRequest):
    token = autenticar(dados.usuario, dados.senha)
    return schemas.LoginResponse(token=token)


@router.post("/logout", status_code=204, dependencies=[Depends(exigir_autenticacao)])
def logout(authorization: str = Header(default="")):
    revogar(authorization)
