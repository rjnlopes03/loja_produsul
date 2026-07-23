"""
Validações genéricas de integridade referencial.

Responsabilidades:
- Bloquear operações (ex.: exclusão) quando existirem linhas
  dependentes em outra tabela, com uma mensagem de erro específica.
- Marcar registros como estornados de forma atômica, sem corrida
  entre duas requisições que tentem estornar o mesmo registro.
"""
from fastapi import HTTPException
from sqlalchemy import ColumnElement, func, update
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


def marcar_estornado(db: Session, modelo: type, id_: int) -> bool:
    """Marca um registro como estornado de forma atômica.

    A checagem "ainda não estornado" e a escrita de `estornado_em`
    acontecem em um único UPDATE, evitando que duas requisições
    concorrentes estornem o mesmo registro duas vezes.

    Args:
        db: Sessão do banco de dados.
        modelo: Classe do modelo SQLAlchemy (precisa ter as colunas
            `id` e `estornado_em`).
        id_: Id do registro a marcar.

    Returns:
        True se marcou agora; False se o registro já estava estornado.
    """
    resultado = db.execute(
        update(modelo)
        .where(modelo.id == id_, modelo.estornado_em.is_(None))
        .values(estornado_em=func.now())
    )
    return resultado.rowcount > 0
