"""empty message

Revision ID: 57c41bf10398
Revises: a0ea667cb54c
Create Date: 2020-09-18 06:12:34.982731

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '57c41bf10398'
down_revision = 'a0ea667cb54c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('shows', sa.Column('show_date', sa.Date()))
    op.drop_column('shows', 'date_to')
    op.drop_column('shows', 'date_from')
    op.add_column(
        'tickets',
        sa.Column('transaction_id', sa.String(length=128), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tickets', 'transaction_id')
    op.add_column(
        'shows',
        sa.Column('date_from',
                  postgresql.TIMESTAMP(),
                  autoincrement=False,
                  nullable=False))
    op.add_column(
        'shows',
        sa.Column('date_to',
                  postgresql.TIMESTAMP(),
                  autoincrement=False,
                  nullable=False))
    op.drop_column('shows', 'show_date')
    # ### end Alembic commands ###
