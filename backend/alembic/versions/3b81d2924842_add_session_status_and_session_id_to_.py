"""Add session status and session_id to client

Revision ID: 3b81d2924842
Revises: f77ed37a95aa
Create Date: 2024-06-28 17:04:42.440873

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3b81d2924842'
down_revision: Union[str, None] = 'f77ed37a95aa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():    
    op.add_column('session', sa.Column('status', sa.Enum('STARTED', 'FINISHED', 'CANCELED', name='sessionstatus'), nullable=True, server_default='started'))


def downgrade():
    op.drop_column('session', 'status')
