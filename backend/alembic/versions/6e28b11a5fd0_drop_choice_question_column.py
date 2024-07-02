"""drop choice.question column

Revision ID: 6e28b11a5fd0
Revises: 001412827caf
Create Date: 2024-06-29 15:16:41.828301

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e28b11a5fd0'
down_revision: Union[str, None] = '001412827caf'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('choice', schema=None) as batch_op:
        batch_op.drop_column('question')


def downgrade() -> None:
    op.add_column('choice', sa.Column('question', sa.VARCHAR(), nullable=True))
