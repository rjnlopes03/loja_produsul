from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..auth import exigir_autenticacao
from ..database import get_db
from ..estoque import ajustar_estoque
from ..validacoes import marcar_estornado

router = APIRouter(
    prefix="/movimentacoes", tags=["movimentacoes"], dependencies=[Depends(exigir_autenticacao)]
)


@router.get("/", response_model=list[schemas.Movimentacao])
def listar_movimentacoes(db: Session = Depends(get_db)):
    return (
        db.query(models.Movimentacao)
        .options(joinedload(models.Movimentacao.produto).joinedload(models.Produto.marca))
        .order_by(models.Movimentacao.criado_em.desc())
        .all()
    )


@router.post("/", response_model=schemas.Movimentacao, status_code=201)
def criar_movimentacao(mov: schemas.MovimentacaoCreate, db: Session = Depends(get_db)):
    produto = db.get(models.Produto, mov.produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if not ajustar_estoque(db, mov.produto_id, mov.tipo, mov.quantidade):
        raise HTTPException(status_code=400, detail="Estoque insuficiente")

    db_mov = models.Movimentacao(**mov.model_dump())
    db.add(db_mov)
    db.commit()
    db.refresh(db_mov)
    return db_mov


@router.post("/{mov_id}/estornar", response_model=schemas.Movimentacao, status_code=201)
def estornar_movimentacao(mov_id: int, db: Session = Depends(get_db)):
    mov = db.get(models.Movimentacao, mov_id)
    if not mov:
        raise HTTPException(status_code=404, detail="Movimentação não encontrada")
    if not marcar_estornado(db, models.Movimentacao, mov_id):
        raise HTTPException(status_code=400, detail="Movimentação já foi estornada")

    tipo_reverso = (
        models.TipoMovimentacao.SAIDA
        if mov.tipo == models.TipoMovimentacao.ENTRADA
        else models.TipoMovimentacao.ENTRADA
    )
    if not ajustar_estoque(db, mov.produto_id, tipo_reverso, mov.quantidade):
        raise HTTPException(status_code=400, detail="Estoque insuficiente para estornar")

    db_estorno = models.Movimentacao(
        produto_id=mov.produto_id,
        tipo=tipo_reverso,
        quantidade=mov.quantidade,
        estorno_de_id=mov.id,
    )
    db.add(db_estorno)
    db.commit()
    db.refresh(db_estorno)
    return db_estorno
