import re
from datetime import date, datetime, time, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, update
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, joinedload

from .. import models, schemas
from ..database import get_db
from ..estoque import ajustar_estoque
from ..validacoes import garantir_sem_referencias, marcar_estornado

router = APIRouter(prefix="/clientes", tags=["clientes"])

# Horário de Brasília (sem horário de verão desde 2019).
FUSO_LOJA = timezone(timedelta(hours=-3))
CENTAVO = 0.005


def _data_local(momento: datetime) -> date:
    # O SQLite devolve datas sem fuso; elas são gravadas em UTC.
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=timezone.utc)
    return momento.astimezone(FUSO_LOJA).date()


def _momento(data: date) -> datetime:
    # Lançamentos com data escolhida ficam ao meio-dia, longe da virada do dia.
    # Gravado em UTC, como o CURRENT_TIMESTAMP padrão (o SQLite descarta o fuso).
    return datetime.combine(data, time(12), tzinfo=FUSO_LOJA).astimezone(timezone.utc)


def _vencimento(data_compra: date, dia: int) -> date:
    # A conta do mês vence no dia escolhido do mês seguinte.
    ano, mes = (data_compra.year + 1, 1) if data_compra.month == 12 else (data_compra.year, data_compra.month + 1)
    return date(ano, mes, dia)


def _situacao(cliente: models.Cliente, compras: list, total_pagamentos: float) -> dict:
    """Saldo e status da conta. Pagamentos quitam as compras mais antigas primeiro."""
    hoje = datetime.now(FUSO_LOJA).date()
    # Compras estornadas não contam no saldo.
    compras = [c for c in compras if c.estornado_em is None]
    total_compras = sum(c.valor_total for c in compras)
    saldo = total_compras - total_pagamentos

    valor_vencido = 0.0
    proximo_vencimento: Optional[date] = None
    pagamentos_restantes = total_pagamentos
    if cliente.dia_vencimento:
        for c in sorted(compras, key=lambda c: c.criado_em):
            aberto = c.valor_total - min(pagamentos_restantes, c.valor_total)
            pagamentos_restantes = max(0.0, pagamentos_restantes - c.valor_total)
            if aberto <= CENTAVO:
                continue
            vencimento = _vencimento(_data_local(c.criado_em), cliente.dia_vencimento)
            if proximo_vencimento is None:
                proximo_vencimento = vencimento
            if vencimento < hoje:
                valor_vencido += aberto

    status_automatico = (
        models.StatusPagamento.ATRASADO if valor_vencido > CENTAVO else models.StatusPagamento.EM_DIA
    )
    return {
        "saldo_devedor": saldo,
        "valor_vencido": valor_vencido,
        "proximo_vencimento": proximo_vencimento,
        "status_automatico": status_automatico,
        "status": cliente.status_manual or status_automatico,
        "acima_do_limite": cliente.limite_credito is not None and saldo > cliente.limite_credito + CENTAVO,
    }


def _obter_cliente(db: Session, cliente_id: int) -> models.Cliente:
    db_cliente = db.get(models.Cliente, cliente_id)
    if not db_cliente:
        raise HTTPException(status_code=404, detail="Cliente não encontrado")
    return db_cliente


def _obter_compra(db: Session, cliente_id: int, compra_id: int) -> models.Compra:
    db_compra = db.get(models.Compra, compra_id)
    if not db_compra or db_compra.cliente_id != cliente_id:
        raise HTTPException(status_code=404, detail="Compra não encontrada")
    return db_compra


def _obter_compra_ativa(db: Session, cliente_id: int, compra_id: int) -> models.Compra:
    # O estorno já devolveu a ração ao estoque; alterar a compra depois disso contaria a devolução duas vezes.
    db_compra = _obter_compra(db, cliente_id, compra_id)
    if db_compra.estornado_em is not None:
        raise HTTPException(status_code=400, detail="Compra estornada não pode ser alterada")
    return db_compra


def _obter_pagamento(db: Session, cliente_id: int, pagamento_id: int) -> models.Pagamento:
    db_pagamento = db.get(models.Pagamento, pagamento_id)
    if not db_pagamento or db_pagamento.cliente_id != cliente_id:
        raise HTTPException(status_code=404, detail="Pagamento não encontrado")
    return db_pagamento


def _salvar_cliente(db: Session, db_cliente: models.Cliente) -> models.Cliente:
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Cliente já cadastrado")
    db.refresh(db_cliente)
    return db_cliente


@router.get("/", response_model=list[schemas.ClienteComSaldo])
def listar_clientes(db: Session = Depends(get_db)):
    clientes = db.query(models.Cliente).order_by(models.Cliente.nome).all()
    compras_por_cliente: dict[int, list] = {}
    for c in db.query(models.Compra).all():
        compras_por_cliente.setdefault(c.cliente_id, []).append(c)
    pagamentos_por_cliente: dict[int, float] = {}
    for p in db.query(models.Pagamento).all():
        pagamentos_por_cliente[p.cliente_id] = pagamentos_por_cliente.get(p.cliente_id, 0) + p.valor

    return [
        schemas.ClienteComSaldo(
            **schemas.Cliente.model_validate(c).model_dump(),
            **_situacao(c, compras_por_cliente.get(c.id, []), pagamentos_por_cliente.get(c.id, 0)),
        )
        for c in clientes
    ]


@router.post("/", response_model=schemas.Cliente, status_code=201)
def criar_cliente(cliente: schemas.ClienteCreate, db: Session = Depends(get_db)):
    if db.query(models.Cliente).filter(models.Cliente.nome == cliente.nome).first():
        raise HTTPException(status_code=400, detail="Cliente já cadastrado")
    db_cliente = models.Cliente(**cliente.model_dump())
    db.add(db_cliente)
    return _salvar_cliente(db, db_cliente)


@router.put("/{cliente_id}", response_model=schemas.Cliente)
def atualizar_cliente(cliente_id: int, cliente: schemas.ClienteUpdate, db: Session = Depends(get_db)):
    db_cliente = _obter_cliente(db, cliente_id)
    dados = cliente.model_dump(exclude_unset=True)
    if "nome" in dados:
        nome = (dados["nome"] or "").strip()
        if not nome:
            raise HTTPException(status_code=400, detail="Informe o nome do cliente")
        outro = db.query(models.Cliente).filter(models.Cliente.nome == nome, models.Cliente.id != cliente_id).first()
        if outro:
            raise HTTPException(status_code=400, detail="Cliente já cadastrado")
        dados["nome"] = nome
    for campo in ("telefone", "observacoes"):
        if campo in dados:
            dados[campo] = (dados[campo] or "").strip() or None
    if dados.get("telefone") and not re.fullmatch(r"[0-9]{1,11}", dados["telefone"]):
        raise HTTPException(status_code=400, detail="O telefone deve ter apenas números (até 11 dígitos, com DDD)")
    for campo, valor in dados.items():
        setattr(db_cliente, campo, valor)
    return _salvar_cliente(db, db_cliente)


@router.delete("/{cliente_id}", status_code=204)
def excluir_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = _obter_cliente(db, cliente_id)
    mensagem = "Não é possível excluir: cliente possui compras ou pagamentos registrados"
    garantir_sem_referencias(db, models.Compra, models.Compra.cliente_id, cliente_id, mensagem)
    garantir_sem_referencias(db, models.Pagamento, models.Pagamento.cliente_id, cliente_id, mensagem)
    db.delete(db_cliente)
    db.commit()


@router.get("/{cliente_id}/resumo", response_model=schemas.ClienteResumo)
def obter_resumo_cliente(cliente_id: int, db: Session = Depends(get_db)):
    db_cliente = _obter_cliente(db, cliente_id)

    compras = (
        db.query(models.Compra)
        .options(joinedload(models.Compra.produto).joinedload(models.Produto.marca))
        .filter(models.Compra.cliente_id == cliente_id)
        .order_by(models.Compra.criado_em.desc(), models.Compra.id.desc())
        .all()
    )
    pagamentos = (
        db.query(models.Pagamento)
        .filter(models.Pagamento.cliente_id == cliente_id)
        .order_by(models.Pagamento.criado_em.desc(), models.Pagamento.id.desc())
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
        **_situacao(db_cliente, compras, total_pagamentos),
    )


@router.post("/{cliente_id}/compras", response_model=schemas.Compra, status_code=201)
def registrar_compra(cliente_id: int, compra: schemas.CompraCreate, db: Session = Depends(get_db)):
    _obter_cliente(db, cliente_id)

    produto = db.get(models.Produto, compra.produto_id)
    if not produto:
        raise HTTPException(status_code=404, detail="Produto não encontrado")

    if not ajustar_estoque(db, compra.produto_id, models.TipoMovimentacao.SAIDA, compra.quantidade):
        raise HTTPException(status_code=400, detail="Estoque insuficiente")

    db.add(
        models.Movimentacao(
            produto_id=produto.id,
            tipo=models.TipoMovimentacao.SAIDA,
            quantidade=compra.quantidade,
            origem=models.OrigemMovimentacao.COMPRA,
        )
    )

    db_compra = models.Compra(
        cliente_id=cliente_id,
        produto_id=compra.produto_id,
        quantidade=compra.quantidade,
        preco_unitario=produto.preco,
    )
    if compra.data:
        db_compra.criado_em = _momento(compra.data)
    db.add(db_compra)
    db.commit()
    db.refresh(db_compra)
    return db_compra


@router.post("/{cliente_id}/compras/{compra_id}/estornar", response_model=schemas.Compra)
def estornar_compra(cliente_id: int, compra_id: int, db: Session = Depends(get_db)):
    compra = _obter_compra(db, cliente_id, compra_id)
    if not marcar_estornado(db, models.Compra, compra_id):
        raise HTTPException(status_code=400, detail="Compra já foi estornada")

    ajustar_estoque(db, compra.produto_id, models.TipoMovimentacao.ENTRADA, compra.quantidade)
    db.add(
        models.Movimentacao(
            produto_id=compra.produto_id,
            tipo=models.TipoMovimentacao.ENTRADA,
            quantidade=compra.quantidade,
            origem=models.OrigemMovimentacao.COMPRA,
        )
    )

    db.commit()
    db.refresh(compra)
    return compra


@router.put("/{cliente_id}/compras/{compra_id}", response_model=schemas.Compra)
def atualizar_compra(cliente_id: int, compra_id: int, compra: schemas.CompraUpdate, db: Session = Depends(get_db)):
    db_compra = _obter_compra_ativa(db, cliente_id, compra_id)

    if compra.quantidade is not None and compra.quantidade != db_compra.quantidade:
        # A diferença sai do (ou volta ao) estoque, com a movimentação correspondente.
        diferenca = compra.quantidade - db_compra.quantidade
        # Só grava se a compra ainda está como foi lida: outra edição, exclusão ou estorno
        # simultâneo faria a diferença ser aplicada ao estoque duas vezes.
        resultado = db.execute(
            update(models.Compra)
            .where(
                models.Compra.id == compra_id,
                models.Compra.quantidade == db_compra.quantidade,
                models.Compra.estornado_em.is_(None),
            )
            .values(quantidade=compra.quantidade)
        )
        if resultado.rowcount == 0:
            raise HTTPException(status_code=409, detail="A compra foi alterada por outra ação. Recarregue a página.")
        tipo = models.TipoMovimentacao.SAIDA if diferenca > 0 else models.TipoMovimentacao.ENTRADA
        if not ajustar_estoque(db, db_compra.produto_id, tipo, abs(diferenca)):
            raise HTTPException(status_code=400, detail="Estoque insuficiente")
        db.add(
            models.Movimentacao(produto_id=db_compra.produto_id, tipo=tipo, quantidade=abs(diferenca), origem=models.OrigemMovimentacao.COMPRA)
        )

    if compra.preco_unitario is not None:
        db_compra.preco_unitario = compra.preco_unitario
    if compra.data:
        db_compra.criado_em = _momento(compra.data)

    db.commit()
    db.refresh(db_compra)
    return db_compra


@router.delete("/{cliente_id}/compras/{compra_id}", status_code=204)
def excluir_compra(cliente_id: int, compra_id: int, db: Session = Depends(get_db)):
    db_compra = _obter_compra_ativa(db, cliente_id, compra_id)
    produto_id, quantidade = db_compra.produto_id, db_compra.quantidade
    # Checagem e exclusão num único DELETE: com dois pedidos simultâneos (ou um estorno),
    # só um apaga a compra e devolve a ração ao estoque.
    resultado = db.execute(
        delete(models.Compra).where(models.Compra.id == compra_id, models.Compra.estornado_em.is_(None))
    )
    if resultado.rowcount == 0:
        raise HTTPException(status_code=400, detail="Compra já foi estornada ou excluída")
    db.expunge(db_compra)
    ajustar_estoque(db, produto_id, models.TipoMovimentacao.ENTRADA, quantidade)
    db.add(
        models.Movimentacao(
            produto_id=produto_id, tipo=models.TipoMovimentacao.ENTRADA, quantidade=quantidade, origem=models.OrigemMovimentacao.COMPRA
        )
    )
    db.commit()


@router.post("/{cliente_id}/pagamentos", response_model=schemas.Pagamento, status_code=201)
def registrar_pagamento(cliente_id: int, pagamento: schemas.PagamentoCreate, db: Session = Depends(get_db)):
    _obter_cliente(db, cliente_id)

    db_pagamento = models.Pagamento(cliente_id=cliente_id, valor=pagamento.valor)
    if pagamento.data:
        db_pagamento.criado_em = _momento(pagamento.data)
    db.add(db_pagamento)
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento


@router.put("/{cliente_id}/pagamentos/{pagamento_id}", response_model=schemas.Pagamento)
def atualizar_pagamento(
    cliente_id: int, pagamento_id: int, pagamento: schemas.PagamentoUpdate, db: Session = Depends(get_db)
):
    db_pagamento = _obter_pagamento(db, cliente_id, pagamento_id)
    if pagamento.valor is not None:
        db_pagamento.valor = pagamento.valor
    if pagamento.data:
        db_pagamento.criado_em = _momento(pagamento.data)
    db.commit()
    db.refresh(db_pagamento)
    return db_pagamento


@router.delete("/{cliente_id}/pagamentos/{pagamento_id}", status_code=204)
def excluir_pagamento(cliente_id: int, pagamento_id: int, db: Session = Depends(get_db)):
    db_pagamento = _obter_pagamento(db, cliente_id, pagamento_id)
    db.delete(db_pagamento)
    db.commit()
