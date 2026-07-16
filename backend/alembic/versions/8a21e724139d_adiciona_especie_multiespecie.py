"""adiciona especie multiespecie

Revision ID: 8a21e724139d
Revises: 3753bd0b8a20
Create Date: 2026-07-16 12:52:42.058691

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a21e724139d'
down_revision: Union[str, Sequence[str], None] = '3753bd0b8a20'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Novo valor "multiespecie" no enum Especie (models.py). A coluna
    # produtos.especie é VARCHAR sem CHECK constraint no SQLite, então o
    # novo valor já é aceito sem alteração de schema.
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
