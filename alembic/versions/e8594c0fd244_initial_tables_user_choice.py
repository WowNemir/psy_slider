"""initial tables user, choice

Revision ID: e8594c0fd244
Revises: 
Create Date: 2024-04-19 00:41:43.643307

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e8594c0fd244'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade():
    # Create User table
    op.create_table('user',
        sa.Column('id', sa.String(length=50), nullable=False),
        sa.Column('role', sa.String(length=10), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    # Create Choice table
    op.create_table('choice',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('choice', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    # Drop Choice table
    op.drop_table('choice')

    # Drop User table
    op.drop_table('user')