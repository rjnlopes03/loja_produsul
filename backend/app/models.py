import enum

from sqlalchemy import Column, Integer, String, Float, Boolean, Enum, ForeignKey, DateTime, func
from sqlalchemy.orm import relationship

from .database import Base


class Especie(str, enum.Enum):
    CACHORRO = "cachorro"
    GATO = "gato"
    COELHO = "coelho"
    GALINHA = "galinha"
    CAVALO = "cavalo"
    VACA = "vaca"
    MULTIESPECIE = "multiespecie"


class FaseVida(str, enum.Enum):
    FILHOTE = "filhote"
    ADULTO = "adulto"
    SENIOR = "senior"
    QUALQUER = "qualquer"


class Marca(Base):
    __tablename__ = "marcas"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False)

    produtos = relationship("Produto", back_populates="marca")


class Produto(Base):
    __tablename__ = "produtos"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, nullable=False)
    marca_id = Column(Integer, ForeignKey("marcas.id"), nullable=False)
    especie = Column(Enum(Especie, native_enum=False), nullable=False)
    fase_vida = Column(Enum(FaseVida, native_enum=False), nullable=False)
    castrado = Column(Boolean, nullable=True)
    peso_kg = Column(Float, nullable=False)
    preco = Column(Float, nullable=False)
    quantidade_estoque = Column(Integer, nullable=False, default=0)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    marca = relationship("Marca", back_populates="produtos")
    movimentacoes = relationship("Movimentacao", back_populates="produto")


class TipoMovimentacao(str, enum.Enum):
    ENTRADA = "entrada"
    SAIDA = "saida"


class Movimentacao(Base):
    __tablename__ = "movimentacoes"

    id = Column(Integer, primary_key=True, index=True)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    tipo = Column(Enum(TipoMovimentacao, native_enum=False), nullable=False)
    quantidade = Column(Integer, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    produto = relationship("Produto", back_populates="movimentacoes")


class StatusPagamento(str, enum.Enum):
    EM_DIA = "em_dia"
    ATRASADO = "atrasado"


class Cliente(Base):
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, unique=True, nullable=False)
    telefone = Column(String, nullable=True)
    observacoes = Column(String, nullable=True)
    limite_credito = Column(Float, nullable=True)
    # Dia do mês (1 a 28) em que vence a conta das compras do mês anterior.
    dia_vencimento = Column(Integer, nullable=True)
    # Quando preenchido, substitui o status calculado pelo vencimento.
    status_manual = Column(Enum(StatusPagamento, native_enum=False), nullable=True)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    compras = relationship("Compra", back_populates="cliente")
    pagamentos = relationship("Pagamento", back_populates="cliente")


class Compra(Base):
    __tablename__ = "compras"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    produto_id = Column(Integer, ForeignKey("produtos.id"), nullable=False)
    quantidade = Column(Integer, nullable=False)
    preco_unitario = Column(Float, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    cliente = relationship("Cliente", back_populates="compras")
    produto = relationship("Produto")

    @property
    def valor_total(self):
        return self.preco_unitario * self.quantidade


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id = Column(Integer, primary_key=True, index=True)
    cliente_id = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    valor = Column(Float, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    cliente = relationship("Cliente", back_populates="pagamentos")
