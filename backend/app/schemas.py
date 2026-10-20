from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .models import Especie, FaseVida, OrigemMovimentacao, StatusPagamento, TipoMovimentacao


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
    # As restrições ficam só na entrada: produtos gravados antes delas não podem derrubar as listagens.
    peso_kg: float = Field(gt=0)
    preco: float = Field(gt=0)
    quantidade_estoque: int = Field(default=0, ge=0)


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
    origem: OrigemMovimentacao
    produto: Produto


class ClienteBase(BaseModel):
    nome: str


class ClienteCreate(ClienteBase):
    pass


class ClienteUpdate(BaseModel):
    nome: Optional[str] = None
    telefone: Optional[str] = None
    observacoes: Optional[str] = None
    limite_credito: Optional[float] = Field(default=None, ge=0)
    dia_vencimento: Optional[int] = Field(default=None, ge=1, le=28)
    # null = status automático (pelo vencimento)
    status_manual: Optional[StatusPagamento] = None


class Cliente(ClienteBase):
    model_config = ConfigDict(from_attributes=True)
    id: int
    telefone: Optional[str] = None
    observacoes: Optional[str] = None
    limite_credito: Optional[float] = None
    dia_vencimento: Optional[int] = None
    status_manual: Optional[StatusPagamento] = None
    criado_em: datetime


class SituacaoConta(BaseModel):
    saldo_devedor: float
    valor_vencido: float
    # Vencimento da compra mais antiga ainda não paga.
    proximo_vencimento: Optional[date] = None
    status_automatico: StatusPagamento
    status: StatusPagamento
    acima_do_limite: bool


class ClienteComSaldo(Cliente, SituacaoConta):
    pass


class CompraCreate(BaseModel):
    produto_id: int
    quantidade: int = Field(gt=0)
    data: Optional[date] = None


class CompraUpdate(BaseModel):
    quantidade: Optional[int] = Field(default=None, gt=0)
    preco_unitario: Optional[float] = Field(default=None, ge=0)
    data: Optional[date] = None


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
    data: Optional[date] = None


class PagamentoUpdate(BaseModel):
    valor: Optional[float] = Field(default=None, gt=0)
    data: Optional[date] = None


class Pagamento(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    cliente_id: int
    valor: float
    criado_em: datetime


class ClienteResumo(SituacaoConta):
    cliente: Cliente
    compras: list[Compra]
    pagamentos: list[Pagamento]
    total_compras: float
    total_pagamentos: float
