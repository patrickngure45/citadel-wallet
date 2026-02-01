"""add cex config manually

Revision ID: f8a9b2c3d4e5
Revises: 2e840597c287
Create Date: 2026-01-31 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'f8a9b2c3d4e5'
down_revision = '2e840597c287'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('users', sa.Column('cex_config', sa.JSON(), nullable=True))


def downgrade():
    op.drop_column('users', 'cex_config')
