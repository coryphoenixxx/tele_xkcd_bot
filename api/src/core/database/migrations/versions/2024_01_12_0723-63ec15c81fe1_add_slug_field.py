"""Add slug field

Revision ID: 63ec15c81fe1
Revises: 6fa68e25fa98
Create Date: 2024-01-12 07:23:57.857017

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '63ec15c81fe1'
down_revision = '6fa68e25fa98'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('comics', sa.Column('slug', sa.String(), nullable=False))
    op.create_unique_constraint(op.f('uq_comics_slug'), 'comics', ['slug'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(op.f('uq_comics_slug'), 'comics', type_='unique')
    op.drop_column('comics', 'slug')
    # ### end Alembic commands ###
