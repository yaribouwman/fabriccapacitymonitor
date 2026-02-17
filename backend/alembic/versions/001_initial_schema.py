"""initial schema

Revision ID: 001
Revises: 
Create Date: 2026-02-16

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'customers',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('name', sa.Text(), nullable=False),
        sa.Column('tenant_id', sa.String(length=36), nullable=False),
        sa.Column('client_id', sa.String(length=36), nullable=False),
        sa.Column('client_secret_ref', sa.Text(), nullable=False),
        sa.Column('subscription_id', sa.String(length=36), nullable=False),
        sa.Column('resource_group', sa.Text(), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.text('true')),
        sa.Column('ingest_key', sa.String(length=64), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('ingest_key')
    )

    op.create_table(
        'capacities',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, server_default=sa.text('gen_random_uuid()')),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('azure_resource_id', sa.Text(), nullable=False),
        sa.Column('display_name', sa.Text(), nullable=True),
        sa.Column('sku_name', sa.String(length=20), nullable=True),
        sa.Column('sku_tier', sa.String(length=20), nullable=True),
        sa.Column('location', sa.String(length=50), nullable=True),
        sa.Column('state', sa.String(length=50), nullable=True),
        sa.Column('last_synced_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('azure_resource_id'),
        sa.UniqueConstraint('customer_id', 'azure_resource_id', name='uq_customer_resource')
    )

    op.create_table(
        'capacity_snapshots',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('capacity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('collected_at', sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column('state', sa.String(length=50), nullable=False),
        sa.Column('sku_name', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['capacity_id'], ['capacities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_snapshot_capacity_time', 'capacity_snapshots', ['capacity_id', 'collected_at'])

    op.create_table(
        'capacity_metrics',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('customer_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('capacity_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('collected_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('aggregation_type', sa.String(length=20), nullable=True),
        sa.ForeignKeyConstraint(['customer_id'], ['customers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['capacity_id'], ['capacities.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_metric_customer_time', 'capacity_metrics', ['customer_id', 'collected_at'])
    op.create_index('ix_metric_capacity_name_time', 'capacity_metrics', ['capacity_id', 'metric_name', 'collected_at'])


def downgrade() -> None:
    op.drop_index('ix_metric_capacity_name_time', table_name='capacity_metrics')
    op.drop_index('ix_metric_customer_time', table_name='capacity_metrics')
    op.drop_table('capacity_metrics')
    op.drop_index('ix_snapshot_capacity_time', table_name='capacity_snapshots')
    op.drop_table('capacity_snapshots')
    op.drop_table('capacities')
    op.drop_table('customers')
