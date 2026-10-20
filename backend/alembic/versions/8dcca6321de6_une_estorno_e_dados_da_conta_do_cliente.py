"""une estorno e dados da conta do cliente

Revision ID: 8dcca6321de6
Revises: 75a2de4c26ad, b5e1c9a4d2f7
Create Date: 2026-10-20 17:23:42.105123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8dcca6321de6'
down_revision: Union[str, Sequence[str], None] = ('75a2de4c26ad', 'b5e1c9a4d2f7')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
