from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from .. import models, schemas
from ..database import get_db

router = APIRouter(prefix="/marcas", tags=["marcas"])


@router.get("/", response_model=list[schemas.Marca])
def listar_marcas(db: Session = Depends(get_db)):
    return db.query(models.Marca).order_by(models.Marca.nome).all()


@router.post("/", response_model=schemas.Marca, status_code=201)
def criar_marca(marca: schemas.MarcaCreate, db: Session = Depends(get_db)):
    if db.query(models.Marca).filter(models.Marca.nome == marca.nome).first():
        raise HTTPException(status_code=400, detail="Marca já cadastrada")
    db_marca = models.Marca(**marca.model_dump())
    db.add(db_marca)
    db.commit()
    db.refresh(db_marca)
    return db_marca


@router.delete("/{marca_id}", status_code=204)
def excluir_marca(marca_id: int, db: Session = Depends(get_db)):
    db_marca = db.query(models.Marca).get(marca_id)
    if not db_marca:
        raise HTTPException(status_code=404, detail="Marca não encontrada")
    db.delete(db_marca)
    db.commit()
