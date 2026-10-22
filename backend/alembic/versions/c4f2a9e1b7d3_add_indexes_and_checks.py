"""adiciona índices nas chaves estrangeiras e CHECKs de quantidades e valores

Revision ID: c4f2a9e1b7d3
Revises: 888cefb7c509
Create Date: 2026-10-22 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c4f2a9e1b7d3'
down_revision: Union[str, Sequence[str], None] = '888cefb7c509'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# (tabela, nome do CHECK, condição)
CHECKS = (
    ("produtos", "ck_produtos_stock_non_negative", "quantidade_estoque >= 0"),
    ("movimentacoes", "ck_movimentacoes_quantity_positive", "quantidade > 0"),
    ("compras", "ck_compras_quantity_positive", "quantidade > 0"),
    ("pagamentos", "ck_pagamentos_amount_positive", "valor > 0"),
)

# (tabela, coluna)
INDEXES = (
    ("compras", "cliente_id"),
    ("compras", "produto_id"),
    ("pagamentos", "cliente_id"),
    ("movimentacoes", "produto_id"),
    ("movimentacoes", "criado_em"),
)


def _ensure_no_violations() -> None:
    """Falha com uma mensagem clara se alguma linha existente violar os CHECKs.

    Raises:
        RuntimeError: Se houver linhas que impediriam criar os CHECKs.
    """
    connection = op.get_bind()
    violations = []
    for table, _, condition in CHECKS:
        count = connection.execute(sa.text(f"SELECT COUNT(*) FROM {table} WHERE NOT ({condition})")).scalar()
        if count:
            violations.append(f"{table}: {count} linha(s) com NOT ({condition})")
    if violations:
        raise RuntimeError("Corrija os dados antes de migrar: " + "; ".join(violations))


def upgrade() -> None:
    """Upgrade schema."""
    _ensure_no_violations()
    # O SQLite não altera constraints direto: o batch recria a tabela (no PostgreSQL vira ALTER TABLE).
    for table, name, condition in CHECKS:
        with op.batch_alter_table(table) as batch_op:
            batch_op.create_check_constraint(name, condition)
    for table, column in INDEXES:
        op.create_index(f"ix_{table}_{column}", table, [column])


def downgrade() -> None:
    """Downgrade schema."""
    for table, column in INDEXES:
        op.drop_index(f"ix_{table}_{column}", table_name=table)
    for table, name, _ in CHECKS:
        with op.batch_alter_table(table) as batch_op:
            batch_op.drop_constraint(name, type_="check")
