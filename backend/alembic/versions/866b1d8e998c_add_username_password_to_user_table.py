"""add username, password to user table

Revision ID: 866b1d8e998c
Revises: e8594c0fd244
Create Date: 2024-04-19 00:46:44.271783

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '866b1d8e998c'
down_revision: Union[str, None] = 'e8594c0fd244'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('user', sa.Column('username', sa.String(length=255), nullable=True))
    op.add_column('user', sa.Column('password', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('user', 'password')
    op.drop_column('user', 'username')
