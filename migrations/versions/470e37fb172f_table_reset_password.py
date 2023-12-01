"""table reset_password 

Revision ID: 470e37fb172f
Revises: d9319c39bb9a
Create Date: 2023-11-30 15:24:24.698029

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '470e37fb172f'
down_revision: Union[str, None] = 'd9319c39bb9a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('reset_password',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('status', postgresql.ENUM('done', 'send', name='status_reset'), nullable=False),
    sa.Column('code', sa.String(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('reset_password')
    op.execute(sa.text('DROP TYPE status_reset'))
    # ### end Alembic commands ###
