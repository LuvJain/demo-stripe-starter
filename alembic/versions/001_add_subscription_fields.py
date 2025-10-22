"""Add subscription fields to User model

Revision ID: 001
Revises:
Create Date: 2025-10-21

"""
from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Add subscription fields to User table
    op.add_column('user', sa.Column('subscription_status', sa.String(), nullable=True))
    op.add_column('user', sa.Column('subscription_tier', sa.String(), nullable=True))
    op.add_column('user', sa.Column('stripe_customer_id', sa.String(), nullable=True))


def downgrade():
    # Remove subscription fields from User table
    op.drop_column('user', 'stripe_customer_id')
    op.drop_column('user', 'subscription_tier')
    op.drop_column('user', 'subscription_status')