"""move share_link to session

Revision ID: 6ebc93bca76d
Revises: 3b81d2924842
Create Date: 2024-06-29 14:38:09.089934

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6ebc93bca76d'
down_revision: Union[str, None] = '3b81d2924842'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('choice', schema=None) as batch_op:
        batch_op.drop_column('share_link')
    with op.batch_alter_table('client', schema=None) as batch_op:
        batch_op.drop_column('session_id')
    op.add_column('session', sa.Column('share_uid', sa.String(length=50), nullable=True))

def downgrade() -> None:
    with op.batch_alter_table('session', schema=None) as batch_op:
        batch_op.drop_column('share_uid')
    op.add_column('client', sa.Column('session_id', sa.INTEGER(), nullable=True))
    op.add_column('choice', sa.Column('share_link', sa.VARCHAR(), nullable=True))
