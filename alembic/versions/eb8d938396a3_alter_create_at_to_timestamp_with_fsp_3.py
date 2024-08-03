"""Alter create_at to TIMESTAMP with fsp=3

Revision ID: eb8d938396a3
Revises: 57f6365531e0
Create Date: 2024-08-03 23:06:59.642103

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


# revision identifiers, used by Alembic.
revision: str = 'eb8d938396a3'
down_revision: Union[str, None] = '57f6365531e0'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Modify the column to have TIMESTAMP with fsp=3
    op.alter_column('post', 'create_at',
                    type_=mysql.TIMESTAMP(fsp=3),
                    existing_type=mysql.TIMESTAMP,
                    nullable=False)


def downgrade() -> None:
    # Revert the column back to TIMESTAMP without fsp
    op.alter_column('post', 'create_at',
                    type_=mysql.TIMESTAMP,
                    existing_type=mysql.TIMESTAMP(fsp=3),
                    nullable=False)
