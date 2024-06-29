"""fix alembic stuff again

Revision ID: 001412827caf
Revises: 745b94b8388d
Create Date: 2024-06-29 15:02:06.788707

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '001412827caf'
down_revision: Union[str, None] = '745b94b8388d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('choice', schema=None) as batch_op:
        batch_op.create_foreign_key('fk_choice_session_id', 'session', ['session_id'], ['id'])
        batch_op.create_foreign_key('fk_choice_client_id', 'client', ['client_id'], ['id'])
        batch_op.create_foreign_key('fk_choice_question_id', 'question', ['question_id'], ['id'])
    
def downgrade() -> None:
    with op.batch_alter_table('choice', schema=None) as batch_op:
        batch_op.drop_constraint('fk_choice_session_id', type_='foreignkey')
        batch_op.drop_constraint('fk_choice_client_id', type_='foreignkey')
        batch_op.drop_constraint('fk_choice_question_id', type_='foreignkey')
