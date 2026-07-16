from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/movimentacoes", tags=["movimentacoes"])


@router.get("/", response_model=list[schemas.Movimentacao])
def listar_movimentacoes(db: Session = Depends(get_db)):
    return db.query(models.Movimentacao).order_by(models.Movimentacao.criado_em.desc()).all()


@router.post("/", response_model=schemas.Movimentacao, status_code=201)
def criar_movimentacao(mov: schemas.MovimentacaoCreate, db: Session = Depends(get_db)):
    produto = db.get(models.Produto, mov.produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if mov.tipo == models.TipoMovimentacao.SAIDA and produto.quantidade_estoque < mov.quantidade:
        raise HTTPException(status_code=400, detail="Estoque insuficiente")

    if mov.tipo == models.TipoMovimentacao.ENTRADA:
        produto.quantidade_estoque += mov.quantidade
    else:
        produto.quantidade_estoque -= mov.quantidade

    db_mov = models.Movimentacao(**mov.model_dump())
    db.add(db_mov)
    db.commit()
    db.refresh(db_mov)
    return db_mov
