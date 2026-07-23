"""
Ajuste atômico de estoque de produtos.

Responsabilidades:
- Aplicar entrada/saída de estoque via UPDATE atômico, evitando a corrida
  entre leitura e escrita da quantidade em estoque quando duas requisições
  concorrentes disputam o mesmo produto.
"""
from sqlalchemy import update
from sqlalchemy.orm import Session

from . import models


def ajustar_estoque(
    db: Session, produto_id: int, tipo: models.TipoMovimentacao, quantidade: int
) -> bool:
    """Aplica entrada ou saída de estoque de forma atômica.

    A checagem de estoque suficiente e o decremento acontecem em uma única
    instrução SQL (`UPDATE ... WHERE quantidade_estoque >= :quantidade`),
    sem uma leitura prévia em Python — por isso não há janela entre
    verificar e escrever onde uma segunda requisição concorrente possa
    intercalar.

    Args:
        db: Sessão do banco de dados.
        produto_id: Id do produto a ajustar.
        tipo: Entrada (soma) ou saída (subtrai) de estoque.
        quantidade: Quantidade a somar ou subtrair.

    Returns:
        True se o ajuste foi aplicado; False se não havia estoque
        suficiente para uma saída (nenhuma linha foi afetada).
    """
    if tipo == models.TipoMovimentacao.ENTRADA:
        stmt = (
            update(models.Produto)
            .where(models.Produto.id == produto_id)
            .values(quantidade_estoque=models.Produto.quantidade_estoque + quantidade)
        )
    else:
        stmt = (
            update(models.Produto)
            .where(
                models.Produto.id == produto_id,
                models.Produto.quantidade_estoque >= quantidade,
            )
            .values(quantidade_estoque=models.Produto.quantidade_estoque - quantidade)
        )
    resultado = db.execute(stmt)
    return resultado.rowcount > 0
