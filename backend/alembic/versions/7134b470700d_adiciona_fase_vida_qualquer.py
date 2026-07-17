"""adiciona fase_vida qualquer

Revision ID: 7134b470700d
Revises: 8a21e724139d
Create Date: 2026-07-16 12:55:52.037027

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7134b470700d'
down_revision: Union[str, Sequence[str], None] = '8a21e724139d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Novo valor "qualquer" no enum FaseVida (models.py). A coluna
    # produtos.fase_vida é VARCHAR sem CHECK constraint no SQLite, então o
    # novo valor já é aceito sem alteração de schema.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
