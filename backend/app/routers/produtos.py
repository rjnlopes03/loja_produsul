from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/produtos", tags=["produtos"])


@router.get("/", response_model=list[schemas.Produto])
def listar_produtos(
    especie: Optional[models.Especie] = None,
    fase_vida: Optional[models.FaseVida] = None,
    castrado: Optional[bool] = None,
    marca_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Produto).options(joinedload(models.Produto.marca))
    if especie:
        if especie == models.Especie.MULTIESPECIE:
            query = query.filter(models.Produto.especie == especie)
        else:
            query = query.filter(
                models.Produto.especie.in_([especie, models.Especie.MULTIESPECIE])
            )
    if fase_vida:
        query = query.filter(models.Produto.fase_vida == fase_vida)
    if castrado is not None:
        query = query.filter(models.Produto.castrado == castrado)
    if marca_id:
        query = query.filter(models.Produto.marca_id == marca_id)
    return query.order_by(models.Produto.nome).all()


@router.get("/{produto_id}", response_model=schemas.Produto)
def obter_produto(produto_id: int, db: Session = Depends(get_db)):
    produto = db.query(models.Produto).options(joinedload(models.Produto.marca)).filter(models.Produto.id == produto_id).first()
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    return produto


@router.post("/", response_model=schemas.Produto, status_code=201)
def criar_produto(produto: schemas.ProdutoCreate, db: Session = Depends(get_db)):
    if not db.get(models.Marca, produto.marca_id):
        raise HTTPException(status_code=400, detail="Marca inválida")
    db_produto = models.Produto(**produto.model_dump())
    db.add(db_produto)
    db.commit()
    db.refresh(db_produto)
    return db_produto


@router.put("/{produto_id}", response_model=schemas.Produto)
def atualizar_produto(produto_id: int, produto: schemas.ProdutoUpdate, db: Session = Depends(get_db)):
    db_produto = db.get(models.Produto, produto_id)
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    for campo, valor in produto.model_dump(exclude_unset=True).items():
        setattr(db_produto, campo, valor)
    db.commit()
    db.refresh(db_produto)
    return db_produto


@router.delete("/{produto_id}", status_code=204)
def excluir_produto(produto_id: int, db: Session = Depends(get_db)):
    db_produto = db.get(models.Produto, produto_id)
    if not db_produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")
    db.delete(db_produto)
    db.commit()
