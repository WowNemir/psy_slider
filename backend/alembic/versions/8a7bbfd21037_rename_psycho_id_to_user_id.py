"""rename psycho_id to user_id

Revision ID: 8a7bbfd21037
Revises: 6e28b11a5fd0
Create Date: 2024-06-29 16:17:48.852847

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8a7bbfd21037'
down_revision: Union[str, None] = '6e28b11a5fd0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.alter_column('psycho_id', new_column_name='user_id')

def downgrade() -> None:
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.alter_column('user_id', new_column_name='psycho_id')
