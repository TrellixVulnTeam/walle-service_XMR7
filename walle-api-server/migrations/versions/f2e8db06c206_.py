"""empty message

Revision ID: f2e8db06c206
Revises: 6859dfbb1682
Create Date: 2016-06-17 12:10:52.741848

"""

# revision identifiers, used by Alembic.
revision = 'f2e8db06c206'
down_revision = '6859dfbb1682'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('allowed_service_urls',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('service_url', sa.String(), nullable=True),
    sa.Column('tenant', sa.String(), nullable=True),
    sa.Column('info', sa.String(), nullable=True),
    sa.Column('created_at', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('service_url_to_cloudify_with_limits',
    sa.Column('id', sa.String(), nullable=False),
    sa.Column('deployment_limits', sa.Integer(), nullable=True),
    sa.Column('number_of_deployments', sa.Integer(), nullable=True),
    sa.Column('cloudify_host', sa.String(), nullable=True),
    sa.Column('cloudify_port', sa.String(), nullable=True),
    sa.Column('created_at', sa.String(), nullable=True),
    sa.Column('updated_at', sa.String(), nullable=True),
    sa.Column('serviceurl_id', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['serviceurl_id'], ['allowed_service_urls.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('allowed_ketstore_urls')
    op.drop_table('allowed_org_ids')
    op.drop_table('org_id_to_cloudify_with_limits')
    op.drop_table('keystore_url_to_cloudify_with_limits')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('keystore_url_to_cloudify_with_limits',
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('keystore_url', sa.VARCHAR(), nullable=True),
    sa.Column('deployment_limits', sa.INTEGER(), nullable=True),
    sa.Column('number_of_deployments', sa.INTEGER(), nullable=True),
    sa.Column('cloudify_host', sa.VARCHAR(), nullable=True),
    sa.Column('cloudify_port', sa.VARCHAR(), nullable=True),
    sa.Column('created_at', sa.VARCHAR(), nullable=True),
    sa.Column('updated_at', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('keystore_url')
    )
    op.create_table('org_id_to_cloudify_with_limits',
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('org_id', sa.VARCHAR(), nullable=False),
    sa.Column('deployment_limits', sa.INTEGER(), nullable=True),
    sa.Column('number_of_deployments', sa.INTEGER(), nullable=True),
    sa.Column('cloudify_host', sa.VARCHAR(), nullable=True),
    sa.Column('cloudify_port', sa.VARCHAR(), nullable=True),
    sa.Column('created_at', sa.DATE(), nullable=True),
    sa.Column('updated_at', sa.DATE(), nullable=True),
    sa.ForeignKeyConstraint(['org_id'], [u'allowed_org_ids.org_id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('org_id')
    )
    op.create_table('allowed_org_ids',
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('org_id', sa.VARCHAR(), nullable=True),
    sa.Column('info', sa.VARCHAR(), nullable=True),
    sa.Column('created_at', sa.DATE(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('org_id')
    )
    op.create_table('allowed_ketstore_urls',
    sa.Column('id', sa.VARCHAR(), nullable=False),
    sa.Column('keystore_url', sa.VARCHAR(), nullable=True),
    sa.Column('info', sa.VARCHAR(), nullable=True),
    sa.Column('created_at', sa.VARCHAR(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('keystore_url')
    )
    op.drop_table('service_url_to_cloudify_with_limits')
    op.drop_table('allowed_service_urls')
    ### end Alembic commands ###
