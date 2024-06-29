"""fix alembic stuff

Revision ID: 745b94b8388d
Revises: 6ebc93bca76d
Create Date: 2024-06-29 14:55:45.922588

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '745b94b8388d'
down_revision: Union[str, None] = '6ebc93bca76d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('choice', schema=None) as batch_op:
        batch_op.alter_column('id',
               existing_type=sa.INTEGER(),
               nullable=False,
               autoincrement=True)
        batch_op.alter_column('client_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
        batch_op.alter_column('user_id',
               existing_type=sa.VARCHAR(),
               nullable=False)
    
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.alter_column('psycho_id',
               existing_type=sa.VARCHAR(length=50),
               nullable=False)


def downgrade() -> None:
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.alter_column('psycho_id',
                existing_type=sa.VARCHAR(length=50),
                nullable=True)
    
    with op.batch_alter_table('choice', schema=None) as batch_op:
        batch_op.alter_column('user_id',
                existing_type=sa.VARCHAR(),
                nullable=True)
        batch_op.alter_column('client_id',
                existing_type=sa.VARCHAR(),
                nullable=True)
        batch_op.alter_column('id',
                existing_type=sa.INTEGER(),
                nullable=True,
                autoincrement=True)
