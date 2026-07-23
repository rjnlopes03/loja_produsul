from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..database import get_db
from ..estoque import ajustar_estoque
from ..validacoes import garantir_sem_referencias, marcar_estornado

router = APIRouter(prefix="/clientes", tags=["clientes"])


def _saldo_devedor(db: Session, cliente_id: int) -> float:
    total_compras = (
        db.query(func.sum(models.Compra.preco_unitario * models.Compra.quantidade))
        .filter(models.Compra.cliente_id == cliente_id, models.Compra.estornado_em.is_(None))
        .scalar()
        or 0
    )
    total_pagamentos = (
        db.query(func.sum(models.Pagamento.valor)).filter(models.Pagamento.cliente_id == cliente_id).scalar() or 0
    )
    return total_compras - total_pagamentos


@router.get("/", response_model=list[schemas.ClienteComSaldo])
def listar_clientes(db: Session = Depends(get_db)):
    clientes = db.query(models.Cliente).order_by(models.Cliente.nome).all()
    return [
        schemas.ClienteComSaldo(
            id=c.id, nome=c.nome, criado_em=c.criado_em, saldo_devedor=_saldo_devedor(db, c.id)
        )
        for c in clientes
    ]


@router.post("/", response_model=schemas.Cliente, status_code=201)
def criar_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    if db.query(models.Cliente).filter(models.Cliente.nome == cliente.nome).first():
        raise HTTPException(status_code=400, detail="Cliente já cadastrado")
    db_cliente = models.Cliente(**cliente.model_dump())
    db.add(db_cliente)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cliente já cadastrado")
    db.refresh(db_cliente)
    return db_cliente


@router.delete("/{cliente_id}", status_code=204)
def excluir_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = db.get(models.Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    mensagem = "Não é possível excluir: cliente possui compras ou pagamentos registrados"
    garantir_sem_referencias(db, models.Compra, models.Compra.cliente_id, cliente_id, mensagem)
    garantir_sem_referencias(db, models.Pagamento, models.Pagamento.cliente_id, cliente_id, mensagem)
    db.delete(db_cliente)
    db.commit()


@router.get("/{cliente_id}/resumo", response_model=schemas.ClienteResumo)
def obter_resumo_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = db.get(models.Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    compras = (
        db.query(models.Compra)
        .options(joinedload(models.Compra.produto).joinedload(models.Produto.marca))
        .filter(models.Compra.cliente_id == cliente_id)
        .order_by(models.Compra.criado_em.desc())
        .all()
    )
    pagamentos = (
        db.query(models.Pagamento)
        .filter(models.Pagamento.cliente_id == cliente_id)
        .order_by(models.Pagamento.criado_em.desc())
        .all()
    )

    total_compras = sum(c.valor_total for c in compras if c.estornado_em is None)
    total_pagamentos = sum(p.valor for p in pagamentos)

    return schemas.ClienteResumo(
        cliente=db_cliente,
        compras=compras,
        pagamentos=pagamentos,
        total_compras=total_compras,
        total_pagamentos=total_pagamentos,
        saldo_devedor=_saldo_devedor(db, cliente_id),
    )


@router.post("/{cliente_id}/compras", response_model=schemas.Compra, status_code=201)
def registrar_compra(cliente_id: int, compra: schemas.CompraCreate, db: Session = Depends(get_db)):
    db_cliente = db.get(models.Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    produto = db.get(models.Produto, compra.produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if not ajustar_estoque(db, compra.produto_id, models.TipoMovimentacao.SAIDA, compra.quantidade):
        raise HTTPException(status_code=400, detail="Estoque insuficiente")

    db.add(models.Movimentacao(produto_id=produto.id, tipo=models.TipoMovimentacao.SAIDA, quantidade=compra.quantidade))

    db_compra = models.Compra(
        cliente_id=cliente_id,
        produto_id=compra.produto_id,
        quantidade=compra.quantidade,
        preco_unitario=produto.preco,
    )
    db.add(db_compra)
    db.commit()
    db.refresh(db_compra)
    return db_compra


@router.post("/{cliente_id}/compras/{compra_id}/estornar", response_model=schemas.Compra)
def estornar_compra(cliente_id: int, compra_id: int, db: Session = Depends(get_db)):
    compra = db.get(models.Compra, compra_id)
    if not compra or compra.cliente_id != cliente_id:
        raise HTTPException(status_code=404, detail="Compra não encontrada")
    if not marcar_estornado(db, models.Compra, compra_id):
        raise HTTPException(status_code=400, detail="Compra já foi estornada")

    ajustar_estoque(db, compra.produto_id, models.TipoMovimentacao.ENTRADA, compra.quantidade)
    db.add(
        models.Movimentacao(
            produto_id=compra.produto_id,
            tipo=models.TipoMovimentacao.ENTRADA,
            quantidade=compra.quantidade,
        )
    )

    db.commit()
    db.refresh(compra)
    return compra


@router.post("/{cliente_id}/pagamentos", response_model=schemas.Pagamento, status_code=201)
def registrar_pagamento(cliente_id: int, pagamento: schemas.PagamentoCreate, db: Session = Depends(get_db)):
    db_cliente = db.get(models.Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")

    db_pagamento = models.Pagamento(cliente_id=cliente_id, valor=pagamento.valor)
    db.add(db_pagamento)
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento
