"""create clothing_items

Revision ID: 7a6b1d84aea4
Revises:
Create Date: 2026-10-07 15:52:29.999631

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "7a6b1d84aea4"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "ClothingItem",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("item_name", sa.String(100), nullable=False),
        sa.Column("item_color", sa.String(20), nullable=False),
        sa.Column("item_size", sa.String(10), nullable=False),
        sa.Column("item_category", sa.String(20), nullable=False),
        sa.Column("item_subcategory", sa.String(50), nullable=False),
        sa.Column("item_image_path", sa.String(255), nullable=False),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("ClothingItem")
