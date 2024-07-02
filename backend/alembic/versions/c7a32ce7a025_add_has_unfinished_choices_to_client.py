"""add has_unfinished_choices to client

Revision ID: c7a32ce7a025
Revises: 35484948a9e9
Create Date: 2024-04-25 00:00:45.183093

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c7a32ce7a025'
down_revision: Union[str, None] = '35484948a9e9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('client', sa.Column('has_unfinished_choices', sa.Boolean, default=False))


def downgrade():
    op.drop_column('client', 'has_unfinished_choices')