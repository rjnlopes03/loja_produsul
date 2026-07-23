from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import Especie, FaseVida, TipoMovimentacao


class LoginRequest(BaseModel):
    usuario: str
    senha: str


class LoginResponse(BaseModel):
    token: str


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
    peso_kg: float = Field(gt=0)
    preco: float = Field(gt=0)
    quantidade_estoque: int = Field(default=0, ge=0)


class ProdutoCreate(ProdutoBase):
    pass


class ProdutoUpdate(BaseModel):
    nome: Optional[str] = None
    marca_id: Optional[int] = None
    especie: Optional[Especie] = None
    fase_vida: Optional[FaseVida] = None
    castrado: Optional[bool] = None
    peso_kg: Optional[float] = Field(default=None, gt=0)
    preco: Optional[float] = Field(default=None, gt=0)


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
    estornado_em: Optional[datetime] = None
    estorno_de_id: Optional[int] = None
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
    estornado_em: Optional[datetime] = None
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
