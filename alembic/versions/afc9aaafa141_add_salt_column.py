"""add salt column

Revision ID: afc9aaafa141
Revises: 866b1d8e998c
Create Date: 2024-04-21 21:07:42.087363

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'afc9aaafa141'
down_revision: Union[str, None] = '866b1d8e998c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('user', sa.Column('salt', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('user', 'salt')