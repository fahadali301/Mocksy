"""add interview session fields

Revision ID: 4c1f9e8a2b11
Revises: 10d17d4eba71
Create Date: 2026-04-09 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "4c1f9e8a2b11"
down_revision: Union[str, Sequence[str], None] = "10d17d4eba71"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("interviews", sa.Column("cv_id", sa.Integer(), nullable=True))
    op.add_column("interviews", sa.Column("status", sa.String(), nullable=False, server_default="active"))
    op.add_column("interviews", sa.Column("final_score", sa.Integer(), nullable=True))
    op.add_column("interviews", sa.Column("final_feedback", sa.String(), nullable=True))
    op.create_foreign_key("fk_interviews_cv_id_cvs", "interviews", "cvs", ["cv_id"], ["id"])


def downgrade() -> None:
    op.drop_constraint("fk_interviews_cv_id_cvs", "interviews", type_="foreignkey")
    op.drop_column("interviews", "final_feedback")
    op.drop_column("interviews", "final_score")
    op.drop_column("interviews", "status")
    op.drop_column("interviews", "cv_id")


