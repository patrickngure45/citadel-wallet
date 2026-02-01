"""merge_migration_heads

Revision ID: 2e840597c287
Revises: 3d7eb6943d98, d4e5f6g7h8i9
Create Date: 2026-01-31 03:27:41.770784

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2e840597c287'
down_revision: Union[str, Sequence[str], None] = ('3d7eb6943d98', 'd4e5f6g7h8i9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
