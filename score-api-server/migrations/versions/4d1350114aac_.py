"""empty message

Revision ID: 4d1350114aac
Revises: 1dba57a5105b
Create Date: 2015-07-02 14:33:43.446068

"""

# revision identifiers, used by Alembic.
revision = '4d1350114aac'
down_revision = '1dba57a5105b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('allowed_org_ids',
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('org_id', sa.VARCHAR(), nullable=True),
    sa.Column('info', sa.VARCHAR()),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('org_id')
    )
    op.drop_table('allowed_orgs')
    op.drop_table('used_orgs')

    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('allowed_org_ids')
    ### end Alembic commands ###
