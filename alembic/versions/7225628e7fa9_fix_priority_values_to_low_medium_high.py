"""fix priority values to low/medium/high

Revision ID: 7225628e7fa9
Revises: b12d7c7ed484
Create Date: 2026-09-03 09:06:42.928174

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7225628e7fa9'
down_revision: Union[str, Sequence[str], None] = 'b12d7c7ed484'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.drop_constraint('ck_tickets_priority', 'tickets', type_='check')
    op.create_check_constraint(
        'ck_tickets_priority',
        'tickets',
        "priority IN ('low', 'medium', 'high')"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_constraint('ck_tickets_priority', 'tickets', type_='check')
    op.create_check_constraint(
        'ck_tickets_priority',
        'tickets',
        "priority IN ('normal', 'urgent')"
    )