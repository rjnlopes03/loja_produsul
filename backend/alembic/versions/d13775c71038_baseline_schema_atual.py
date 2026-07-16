"""baseline schema atual

Revision ID: d13775c71038
Revises: 
Create Date: 2026-07-16 08:24:57.816833

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd13775c71038'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Marca o schema já existente (criado via Base.metadata.create_all) como baseline.
    # O diff de tipo em produtos.fase_vida é falso positivo do SQLite (não distingue
    # VARCHAR de Enum real), por isso não há operações aqui.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
