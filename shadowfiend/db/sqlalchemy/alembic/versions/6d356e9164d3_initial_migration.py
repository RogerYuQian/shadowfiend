"""initial migration

Revision ID: 6d356e9164d3
Revises: 
Create Date: 2017-10-24 17:31:54.544759

"""

# revision identifiers, used by Alembic.
revision = '6d356e9164d3'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'account',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.String(255), index=True, unique=True),
        sa.Column('domain_id', sa.String(255)),
        sa.Column('balance', sa.DECIMAL(20,4)),
        sa.Column('consumption', sa.DECIMAL(20,4)),
        sa.Column('level', sa.Integer),
        sa.Column('owed', sa.Boolean),
        sa.Column('deleted', sa.Boolean),

        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),
        sa.Column('deleted_at', sa.DateTime),

        mysql_engine='InnoDB',
        mysql_charset='UTF8'
    )

    op.create_table(
        'project',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.String(255), index=True),
        sa.Column('project_id', sa.String(255), index=True, unique=True),
        sa.Column('consumption', sa.DECIMAL(20,4)),

        sa.Column('domain_id', sa.String(255)),

        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),

        mysql_engine='InnoDB',
        mysql_charset='UTF8'
    )

    op.create_table(
        'usr_prj_relation',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('user_id', sa.String(255), index=True),
        sa.Column('project_id', sa.String(255), index=True),
        sa.Column('consumption', sa.DECIMAL(20,4)),

        sa.Column('domain_id', sa.String(255)),

        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),

        mysql_engine='InnoDB',
        mysql_charset='UTF8'
    )

    op.create_unique_constraint('uq_usr_prj_relation_id', 'usr_prj_relation', ['user_id', 'project_id'])

    op.create_table(
        'charge',
        sa.Column('id', sa.Integer, primary_key=True),
        sa.Column('charge_id', sa.String(255)),
        sa.Column('user_id', sa.String(255), unique=True),
        sa.Column('domain_id', sa.String(255)),
        sa.Column('value', sa.DECIMAL(20,4)),
        sa.Column('type', sa.String(64)),
        sa.Column('come_from', sa.String(255)),
        sa.Column('charge_time', sa.DateTime),
        sa.Column('remarks', sa.String(255)),

        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),

        mysql_engine='InnoDB',
        mysql_charset='UTF8'
    )

    op.create_table(
        'order',

        sa.Column('id', sa.Integer, primary_key=True),

        sa.Column('order_id', sa.String(255), index=True),
        sa.Column('resource_id', sa.String(255), index=True, unique=True),
        sa.Column('resource_name', sa.String(255)),

        sa.Column('type', sa.String(255)),
        sa.Column('status', sa.String(64)),

        sa.Column('unit_price', sa.DECIMAL(20,4)),
        sa.Column('unit', sa.String(64)),
        sa.Column('total_price', sa.DECIMAL(20,4)),
        sa.Column('cron_time', sa.DateTime),
        sa.Column('date_time', sa.DateTime),

        sa.Column('renew', sa.Boolean),
        sa.Column('renew_method', sa.String(64)),
        sa.Column('renew_period', sa.Integer),

        sa.Column('user_id', sa.String(255), index=True),
        sa.Column('project_id', sa.String(255), index=True),
        sa.Column('region_id', sa.String(255)),
        sa.Column('domain_id', sa.String(255)),

        sa.Column('charged', sa.Boolean),
        sa.Column('owed', sa.Boolean),

        sa.Column('created_at', sa.DateTime),
        sa.Column('updated_at', sa.DateTime),

        mysql_engine='InnoDB',
        mysql_charset='utf8',
    )
    op.create_index('ix_order_user_id_project_id', 'order', ['user_id', 'project_id'])
    op.create_unique_constraint('uq_order_resource_id', 'order', ['order_id', 'resource_id'])

