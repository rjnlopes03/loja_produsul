from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import Especie, FaseVida, TipoMovimentacao


class MarcaBase(BaseModel):
    nome: str


class MarcaCreate(MarcaBase):
    pass


class Marca(MarcaBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class ProdutoBase(BaseModel):
    nome: str
    marca_id: int
    especie: Especie
    fase_vida: FaseVida
    castrado: Optional[bool] = None
    peso_kg: float
    preco: float
    quantidade_estoque: int = 0


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    marca_id: Optional[int] = None
    especie: Optional[Especie] = None
    fase_vida: Optional[FaseVida] = None
    castrado: Optional[bool] = None
    peso_kg: Optional[float] = None
    preco: Optional[float] = None
    quantidade_estoque: Optional[int] = None


class Produto(ProdutoBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    criado_em: datetime
    marca: Marca


class MovimentacaoCreate(BaseModel):
    produto_id: int
    tipo: TipoMovimentacao
    quantidade: int = Field(gt=0)


class Movimentacao(MovimentacaoCreate):
    model_config = ConfigDict(from_attributes=True)
    id: int
    criado_em: datetime
    produto: Produto


class ClienteBase(BaseModel):
    nome: str


class ClienteCreate(ClienteBase):
    pass


class Cliente(ClienteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    criado_em: datetime


class ClienteComSaldo(Cliente):
    saldo_devedor: float


class CompraCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)


class Compra(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cliente_id: int
    produto_id: int
    quantidade: int
    preco_unitario: float
    valor_total: float
    criado_em: datetime
    produto: Produto


class PagamentoCreate(BaseModel):
    valor: float = Field(gt=0)


class Pagamento(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cliente_id: int
    valor: float
    criado_em: datetime


class ClienteResumo(BaseModel):
    cliente: Cliente
    compras: list[Compra]
    pagamentos: list[Pagamento]
    total_compras: float
    total_pagamentos: float
    saldo_devedor: float
