"""add customer health tracking

Revision ID: 002
Revises: 001
Create Date: 2026-02-16

"""
from alembic import op
import sqlalchemy as sa

revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('customers', sa.Column('health_status', sa.String(length=20), nullable=False, server_default='healthy'))
    op.add_column('customers', sa.Column('last_successful_collection', sa.DateTime(timezone=True), nullable=True))
    op.add_column('customers', sa.Column('last_collection_error', sa.Text(), nullable=True))
    op.add_column('customers', sa.Column('consecutive_failures', sa.Integer(), nullable=False, server_default='0'))
    
    op.create_index('ix_customers_health_status', 'customers', ['health_status'])


def downgrade() -> None:
    op.drop_index('ix_customers_health_status', table_name='customers')
    op.drop_column('customers', 'consecutive_failures')
    op.drop_column('customers', 'last_collection_error')
    op.drop_column('customers', 'last_successful_collection')
    op.drop_column('customers', 'health_status')
