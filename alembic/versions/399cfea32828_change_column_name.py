"""Change column name

Revision ID: 399cfea32828
Revises: bdf266bdcc71
Create Date: 2024-07-20 20:52:42.142944

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = '399cfea32828'
down_revision: Union[str, None] = 'bdf266bdcc71'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tag', sa.Column('category_id', sa.BIGINT(), nullable=False))
    op.drop_constraint('tag_ibfk_1', 'tag', type_='foreignkey')
    op.create_foreign_key(None, 'tag', 'category', ['category_id'], ['id'])
    op.drop_column('tag', 'category_key')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tag', sa.Column('category_key', mysql.BIGINT(), autoincrement=False, nullable=False))
    op.drop_constraint(None, 'tag', type_='foreignkey')
    op.create_foreign_key('tag_ibfk_1', 'tag', 'category', ['category_key'], ['id'])
    op.drop_column('tag', 'category_id')
    # ### end Alembic commands ###
