"""add_hearing_records

Revision ID: d4e5f6g7h8i9
Revises: f25b0a6bfed2
Create Date: 2026-01-31 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'd4e5f6g7h8i9'
down_revision = 'f25b0a6bfed2'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'hearing_records',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('intent', sa.String(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('transcript', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('final_verdict', sa.String(), nullable=False),
        sa.Column('final_reason', sa.String(), nullable=True),
    )
    op.create_index(op.f('ix_hearing_records_id'), 'hearing_records', ['id'], unique=False)
    op.create_index(op.f('ix_hearing_records_user_id'), 'hearing_records', ['user_id'], unique=False)
    op.create_index(op.f('ix_hearing_records_final_verdict'), 'hearing_records', ['final_verdict'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_hearing_records_final_verdict'), table_name='hearing_records')
    op.drop_index(op.f('ix_hearing_records_user_id'), table_name='hearing_records')
    op.drop_index(op.f('ix_hearing_records_id'), table_name='hearing_records')
    op.drop_table('hearing_records')
