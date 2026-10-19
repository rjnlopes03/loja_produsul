"""adiciona dados da conta do cliente

Revision ID: b5e1c9a4d2f7
Revises: 7134b470700d
Create Date: 2026-10-18 23:10:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b5e1c9a4d2f7'
down_revision: Union[str, Sequence[str], None] = '7134b470700d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('clientes', sa.Column('telefone', sa.String(), nullable=True))
    op.add_column('clientes', sa.Column('observacoes', sa.String(), nullable=True))
    op.add_column('clientes', sa.Column('limite_credito', sa.Float(), nullable=True))
    op.add_column('clientes', sa.Column('dia_vencimento', sa.Integer(), nullable=True))
    # Enum StatusPagamento (models.py), gravado como VARCHAR (native_enum=False).
    op.add_column('clientes', sa.Column('status_manual', sa.String(length=8), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table('clientes') as batch_op:
        batch_op.drop_column('status_manual')
        batch_op.drop_column('dia_vencimento')
        batch_op.drop_column('limite_credito')
        batch_op.drop_column('observacoes')
        batch_op.drop_column('telefone')
