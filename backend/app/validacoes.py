"""
Validações genéricas de integridade referencial.

Responsabilidades:
- Bloquear operações (ex.: exclusão) quando existirem linhas
  dependentes em outra tabela, com uma mensagem de erro específica.
"""
from fastapi import HTTPException
from sqlalchemy import ColumnElement
from sqlalchemy.orm import Session


def garantir_sem_referencias(
    db: Session, modelo: type, campo: ColumnElement, valor: object, mensagem: str
) -> None:
    """Bloqueia a operação se existir alguma linha de `modelo` com `campo == valor`.

    Args:
        db: Sessão do banco de dados.
        modelo: Classe do modelo SQLAlchemy a consultar.
        campo: Coluna do modelo usada no filtro (ex.: Compra.produto_id).
        valor: Valor a comparar no filtro.
        mensagem: Mensagem de erro a retornar se houver referência.

    Raises:
        HTTPException: 400 com `mensagem`, se existir ao menos uma linha.
    """
    if db.query(modelo).filter(campo == valor).count() > 0:
        raise HTTPException(status_code=400, detail=mensagem)
