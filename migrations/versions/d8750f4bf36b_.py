"""empty message

Revision ID: d8750f4bf36b
Revises: c0a6e5c87677
Create Date: 2020-09-15 17:58:12.958954

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd8750f4bf36b'
down_revision = 'c0a6e5c87677'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('tickets',
                  sa.Column('no_of_seats', sa.Integer(), nullable=False))
    op.add_column('tickets', sa.Column('ticket_date',
                                       sa.Date(),
                                       nullable=False))
    op.alter_column('shows',
                    'show_times',
                    existing_type=postgresql.ARRAY(sa.String(length=8)),
                    type_=sa.String(length=8))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('tickets', 'ticket_date')
    op.drop_column('tickets', 'no_of_seats')
    op.alter_column('shows',
                    'show_times',
                    existing_type=sa.String(length=8),
                    type_=sa.String(length=8))
    # ### end Alembic commands ###
