"""add question and share_link columns to choice

Revision ID: 35484948a9e9
Revises: b2cf24325fde
Create Date: 2024-04-24 13:32:31.144865

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '35484948a9e9'
down_revision: Union[str, None] = 'b2cf24325fde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    op.add_column('choice', sa.Column('question', sa.String(length=255), nullable=True))
    op.add_column('choice', sa.Column('share_link', sa.String(length=255), nullable=True))


def downgrade():
    op.drop_column('choice', 'question')
    op.drop_column('choice', 'share_link')
