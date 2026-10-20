"""adiciona origem em movimentacoes

Revision ID: 888cefb7c509
Revises: 8dcca6321de6
Create Date: 2026-10-20 18:12:10.995533

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '888cefb7c509'
down_revision: Union[str, Sequence[str], None] = '8dcca6321de6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Movimentações já existentes ficam como manuais: antes desta coluna não dá para saber
    # quais saíram de uma compra. O Enum grava o nome do membro, por isso "MANUAL".
    op.add_column(
        "movimentacoes",
        sa.Column("origem", sa.String(length=7), nullable=False, server_default="MANUAL"),
    )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("movimentacoes") as batch_op:
        batch_op.drop_column("origem")
