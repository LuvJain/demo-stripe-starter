"""Add subscription fields to User

Revision ID: 20251021_232836
Revises:
Create Date: 2025-10-21 23:28:36

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '20251021_232836'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add the subscription fields to the user table
    op.add_column('user', sa.Column('subscription_status', sa.String(), nullable=True))
    op.add_column('user', sa.Column('subscription_tier', sa.String(), nullable=True))
    op.add_column('user', sa.Column('stripe_customer_id', sa.String(), nullable=True))


def downgrade() -> None:
    # Remove the subscription fields from the user table
    op.drop_column('user', 'stripe_customer_id')
    op.drop_column('user', 'subscription_tier')
    op.drop_column('user', 'subscription_status')