"""remove user.choices add client table

Revision ID: b2cf24325fde
Revises: afc9aaafa141
Create Date: 2024-04-22 01:14:40.341295

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2cf24325fde'
down_revision: Union[str, None] = 'afc9aaafa141'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'client',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('psycho_id', sa.String(length=50), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.add_column('choice', sa.Column('client_id', sa.String(length=50), nullable=True))

def downgrade() -> None:

    op.drop_table('client')
    op.drop_constraint('choices_client_id_fkey', 'choice', type_='foreignkey')
    op.drop_column('choice', 'client_id')