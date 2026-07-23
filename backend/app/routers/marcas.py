from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import models, schemas
from ..auth import exigir_autenticacao
from ..database import get_db
from ..validacoes import garantir_sem_referencias

router = APIRouter(prefix="/marcas", tags=["marcas"], dependencies=[Depends(exigir_autenticacao)])


@router.get("/", response_model=list[schemas.Marca])
def listar_marcas(db: Session = Depends(get_db)):
    return db.query(models.Marca).order_by(models.Marca.nome).all()


@router.post("/", response_model=schemas.Marca, status_code=201)
def criar_marca(marca: schemas.MarcaCreate, db: Session = Depends(get_db)):
    if db.query(models.Marca).filter(models.Marca.nome == marca.nome).first():
        raise HTTPException(status_code=400, detail="Marca já cadastrada")
    db_marca = models.Marca(**marca.model_dump())
    db.add(db_marca)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Marca já cadastrada")
    db.refresh(db_marca)
    return db_marca


@router.delete("/{marca_id}", status_code=204)
def excluir_marca(marca_id: int, db: Session = Depends(get_db)):
    db_marca = db.get(models.Marca, marca_id)
    if not db_marca:
        raise HTTPException(status_code=404, detail="Marca não encontrada")
    garantir_sem_referencias(
        db,
        models.Produto,
        models.Produto.marca_id,
        marca_id,
        "Não é possível excluir: existem produtos cadastrados com esta marca",
    )
    db.delete(db_marca)
    db.commit()
