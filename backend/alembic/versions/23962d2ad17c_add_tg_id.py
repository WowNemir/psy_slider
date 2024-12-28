"""Add telegram_id column

Revision ID: 23962d2ad17c
Revises: 64c629922971
Create Date: 2024-12-28 17:04:34.490323

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '23962d2ad17c'
down_revision: Union[str, None] = '64c629922971'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('user', sa.Column('telegram_id', sa.String(length=255), nullable=True))
    op.create_index(op.f('ix_user_telegram_id'), 'user', ['telegram_id'], unique=True)


def downgrade() -> None:
    op.drop_index(op.f('ix_user_telegram_id'), table_name='user')
    op.drop_column('user', 'telegram_id')
