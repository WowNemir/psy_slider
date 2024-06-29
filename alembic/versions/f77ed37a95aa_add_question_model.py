"""Add Question model

Revision ID: f77ed37a95aa
Revises: 7e0be7a9e679
Create Date: 2024-06-28 14:20:55.650313

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import table, column
from sqlalchemy import String, Integer

# revision identifiers, used by Alembic.
revision: str = 'f77ed37a95aa'
down_revision: Union[str, None] = '7e0be7a9e679'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table('question',
    sa.Column('id', sa.Integer, primary_key=True, autoincrement=True),
    sa.Column('theme', sa.String(length=255), nullable=False),
    sa.Column('text', sa.String(length=255), nullable=False),
    sa.Column('type', sa.String(length=50), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column('choice', sa.Column('question_id', sa.Integer(), nullable=False, server_default='0'))

    question_table = table('question',
        column('theme', String),
        column('text', String),
        column('type', String)
    )

    questions1 = [
        {"theme": "Индивидуально", "text": "Как вы оцениваете ваше индивидуальное благополучие на прошедшей неделе?", "type": "before_session"},
        {"theme": "В личных отношениях", "text": "Как вы оцениваете ваши личные отношения за прошедшую неделю?", "type": "before_session"},
        {"theme": "Социально", "text": "Как вы оцениваете ваше социальное состояние на прошедшей неделе?", "type": "before_session"},
        {"theme": "Личное благополучие", "text": "Как вы оцениваете ваше общее ощущение благополучия на прошедшей неделе?", "type": "before_session"}
    ]

    questions2 = [
        {"theme": 'Отношение', "text": "Чувствовали ли вы, что ваше отношение было положительно оценено и уважаемо?", "type": "after_session"},
        {"theme": 'Цели и темы', "text": "Были ли обсуждены те темы или задачи, которые вы считали важными для данной консультации?", "type": "after_session"},
        {"theme": 'Подход и метод', "text": "Насколько подход и метод работы терапевта соответствовали вашим ожиданиям и предпочтениям?", "type": "after_session"},
        {"theme": 'В целом', "text": "Каково ваше общее впечатление от сегодняшней консультации?", "type": "after_session"}
    ]

    op.bulk_insert(question_table, questions1 + questions2)


def downgrade() -> None:
    op.drop_column('choice', 'question_id')
    op.drop_table('question')