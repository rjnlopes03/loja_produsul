from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "75a2de4c26ad"
down_revision: Union[str, Sequence[str], None] = "7134b470700d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "compras", sa.Column("estornado_em", sa.DateTime(timezone=True), nullable=True)
    )
    op.add_column(
        "movimentacoes",
        sa.Column("estornado_em", sa.DateTime(timezone=True), nullable=True),
    )
    with op.batch_alter_table("movimentacoes") as batch_op:
        batch_op.add_column(sa.Column("estorno_de_id", sa.Integer(), nullable=True))
        batch_op.create_foreign_key(
            "fk_movimentacoes_estorno_de_id_movimentacoes",
            "movimentacoes",
            ["estorno_de_id"],
            ["id"],
        )


def downgrade() -> None:
    """Downgrade schema."""
    with op.batch_alter_table("movimentacoes") as batch_op:
        batch_op.drop_constraint(
            "fk_movimentacoes_estorno_de_id_movimentacoes", type_="foreignkey"
        )
        batch_op.drop_column("estorno_de_id")
    op.drop_column("movimentacoes", "estornado_em")
    op.drop_column("compras", "estornado_em")
