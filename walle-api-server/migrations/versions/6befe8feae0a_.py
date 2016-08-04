"""empty message

Revision ID: 6befe8feae0a
Revises: edf7d155a43b
Create Date: 2016-08-04 15:30:39.946189

"""

# revision identifiers, used by Alembic.
revision = '6befe8feae0a'
down_revision = 'edf7d155a43b'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('approved_plugins_v1',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('source', sa.String(length=2048), nullable=True),
    sa.Column('plugin_type', sa.String(length=32), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('endpoints_v1',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('endpoint', sa.String(length=2048), nullable=True),
    sa.Column('type', sa.String(length=32), nullable=True),
    sa.Column('version', sa.String(length=16), nullable=True),
    sa.Column('description', sa.String(length=1024), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('rights_v1',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=1024), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('walle_admins_v1',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('name', sa.String(length=64), nullable=True),
    sa.Column('password', sa.String(length=32), nullable=True),
    sa.Column('token', sa.String(length=32), nullable=True),
    sa.Column('expire', sa.Integer(), nullable=True),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('tenants_v1',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('tenant_name', sa.String(length=64), nullable=True),
    sa.Column('description', sa.String(length=1024), nullable=True),
    sa.Column('endpoint_id', sa.String(length=36), nullable=True),
    sa.Column('cloudify_host', sa.String(length=2048), nullable=True),
    sa.Column('cloudify_port', sa.Integer(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['endpoint_id'], ['endpoints_v1.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('limits_v1',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('tenant_id', sa.String(length=36), nullable=True),
    sa.Column('soft', sa.Integer(), nullable=True),
    sa.Column('hard', sa.Integer(), nullable=True),
    sa.Column('value', sa.Integer(), nullable=True),
    sa.Column('type', sa.String(length=32), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants_v1.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('tenant_rights_v1',
    sa.Column('id', sa.String(length=36), nullable=False),
    sa.Column('tenant_id', sa.String(length=36), nullable=True),
    sa.Column('rights_id', sa.String(length=36), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['rights_id'], ['rights_v1.id'], ),
    sa.ForeignKeyConstraint(['tenant_id'], ['tenants_v1.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.drop_table('approved_plugins')
    op.drop_table('walle_admins')
    op.drop_table('limits')
    op.drop_table('tenants')
    op.drop_table('endpoints')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('approved_plugins',
    sa.Column('id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('source', sa.VARCHAR(length=255), autoincrement=False, nullable=True),
    sa.Column('plugin_type', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=u'approved_plugins_pkey')
    )
    op.create_table('limits',
    sa.Column('id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('tenant_id', sa.VARCHAR(length=36), autoincrement=False, nullable=True),
    sa.Column('soft', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('hard', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('value', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('type', sa.VARCHAR(length=24), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['tenant_id'], [u'tenants.id'], name=u'limits_tenant_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'limits_pkey')
    )
    op.create_table('tenants',
    sa.Column('id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('tenant_name', sa.VARCHAR(length=64), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(length=1024), autoincrement=False, nullable=True),
    sa.Column('endpoint_id', sa.VARCHAR(length=36), autoincrement=False, nullable=True),
    sa.Column('cloudify_host', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('cloudify_port', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['endpoint_id'], [u'endpoints.id'], name=u'tenants_endpoint_id_fkey'),
    sa.PrimaryKeyConstraint('id', name=u'tenants_pkey'),
    postgresql_ignore_search_path=False
    )
    op.create_table('endpoints',
    sa.Column('id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('endpoint', sa.VARCHAR(length=128), autoincrement=False, nullable=True),
    sa.Column('type', sa.VARCHAR(length=24), autoincrement=False, nullable=True),
    sa.Column('version', sa.VARCHAR(length=16), autoincrement=False, nullable=True),
    sa.Column('description', sa.VARCHAR(length=1024), autoincrement=False, nullable=True),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=u'endpoints_pkey')
    )
    op.create_table('walle_admins',
    sa.Column('id', sa.VARCHAR(length=36), autoincrement=False, nullable=False),
    sa.Column('name', sa.VARCHAR(length=16), autoincrement=False, nullable=True),
    sa.Column('password', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.Column('token', sa.VARCHAR(length=32), autoincrement=False, nullable=True),
    sa.Column('expire', sa.INTEGER(), autoincrement=False, nullable=True),
    sa.PrimaryKeyConstraint('id', name=u'walle_admins_pkey'),
    sa.UniqueConstraint('name', name=u'walle_admins_name_key')
    )
    op.drop_table('limits_v1')
    op.drop_table('tenant_rights_v1')
    op.drop_table('tenants_v1')
    op.drop_table('rights_v1')
    op.drop_table('endpoints_v1')
    op.drop_table('walle_admins_v1')
    op.drop_table('approved_plugins_v1')
    ### end Alembic commands ###
