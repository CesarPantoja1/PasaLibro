"""make message created_at timezone aware

Revision ID: b74c2d7e9a10
Revises: a58fae14eaf7
Create Date: 2026-05-26 02:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b74c2d7e9a10'
down_revision = 'a58fae14eaf7'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        'messages',
        'created_at',
        existing_type=sa.DateTime(),
        type_=sa.DateTime(timezone=True),
        postgresql_using="created_at AT TIME ZONE 'America/Guayaquil'",
        existing_nullable=True
    )


def downgrade():
    op.alter_column(
        'messages',
        'created_at',
        existing_type=sa.DateTime(timezone=True),
        type_=sa.DateTime(),
        postgresql_using="created_at AT TIME ZONE 'America/Guayaquil'",
        existing_nullable=True
    )
