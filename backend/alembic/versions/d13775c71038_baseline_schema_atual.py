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
    op.create_table('marcas',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('nome')
    )
    op.create_index(op.f('ix_marcas_id'), 'marcas', ['id'], unique=False)
    op.create_table('produtos',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nome', sa.String(), nullable=False),
    sa.Column('marca_id', sa.Integer(), nullable=False),
    sa.Column('especie', sa.String(length=12), nullable=False),
    sa.Column('fase_vida', sa.String(length=8), nullable=False),
    sa.Column('castrado', sa.Boolean(), nullable=True),
    sa.Column('peso_kg', sa.Float(), nullable=False),
    sa.Column('preco', sa.Float(), nullable=False),
    sa.Column('quantidade_estoque', sa.Integer(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['marca_id'], ['marcas.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_produtos_id'), 'produtos', ['id'], unique=False)
    op.create_table('movimentacoes',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('produto_id', sa.Integer(), nullable=False),
    sa.Column('tipo', sa.String(length=7), nullable=False),
    sa.Column('quantidade', sa.Integer(), nullable=False),
    sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=True),
    sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_movimentacoes_id'), 'movimentacoes', ['id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_movimentacoes_id'), table_name='movimentacoes')
    op.drop_table('movimentacoes')
    op.drop_index(op.f('ix_produtos_id'), table_name='produtos')
    op.drop_table('produtos')
    op.drop_index(op.f('ix_marcas_id'), table_name='marcas')
    op.drop_table('marcas')
