"""autogenerate user.id

Revision ID: 2f9cb02fd952
Revises: 866b1d8e998c
Create Date: 2024-04-19 00:55:46.819150

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f9cb02fd952'
down_revision: Union[str, None] = '866b1d8e998c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.drop_column('user', 'id')  # Drop the existing id column
    op.execute('ALTER TABLE user ADD COLUMN id INTEGER PRIMARY KEY AUTOINCREMENT')  # Add new auto-generated primary key


def downgrade():
    op.drop_column('user', 'id')  # Drop the auto-generated primary key
    op.add_column('user', sa.Column('id', sa.String(50), primary_key=True))  # Add back the old id column
    