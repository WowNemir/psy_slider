"""Add Session model and relationships

Revision ID: 7e0be7a9e679
Revises: c7a32ce7a025
Create Date: 2024-06-28 00:40:51.341883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7e0be7a9e679'
down_revision: Union[str, None] = 'c7a32ce7a025'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('session',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('client_id', sa.String(length=50), nullable=False),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('pre_session_completed', sa.Boolean(), nullable=True),
    sa.Column('post_session_completed', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['client_id'], ['client.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('choice', sa.Column('session_id', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('choice', 'session_id')
    op.drop_table('session')
