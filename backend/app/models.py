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


class FaseVida(str, enum.Enum):
    FILHOTE = "filhote"
    ADULTO = "adulto"
    SENIOR = "senior"


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
    especie = Column(Enum(Especie), nullable=False)
    fase_vida = Column(Enum(FaseVida), nullable=False)
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
    tipo = Column(Enum(TipoMovimentacao), nullable=False)
    quantidade = Column(Integer, nullable=False)
    criado_em = Column(DateTime(timezone=True), server_default=func.now())

    produto = relationship("Produto", back_populates="movimentacoes")
