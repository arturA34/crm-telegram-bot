"""add teams and clients

Revision ID: 002
Revises: 001
Create Date: 2026-02-22

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create teams table
    op.create_table(
        "teams",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("invite_code", sa.String(length=20), nullable=False),
        sa.Column("owner_id", sa.BigInteger(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("invite_code"),
    )
    op.create_index("ix_teams_invite_code", "teams", ["invite_code"])

    # Add role and team_id to users
    op.add_column(
        "users",
        sa.Column(
            "role", sa.String(length=20), server_default="SOLO", nullable=False
        ),
    )
    op.add_column(
        "users",
        sa.Column("team_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_users_team_id", "users", "teams", ["team_id"], ["id"]
    )

    # Create clients table
    op.create_table(
        "clients",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column("source", sa.String(length=100), nullable=True),
        sa.Column(
            "budget",
            sa.Numeric(precision=12, scale=2),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "status", sa.String(length=20), server_default="NEW", nullable=False
        ),
        sa.Column("manager_id", sa.Integer(), nullable=False),
        sa.Column("team_id", sa.Integer(), nullable=True),
        sa.Column("reminder_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(["manager_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["team_id"], ["teams.id"]),
    )
    op.create_index("ix_clients_manager_id", "clients", ["manager_id"])
    op.create_index("ix_clients_team_id", "clients", ["team_id"])
    op.create_index("ix_clients_status", "clients", ["status"])
    op.create_index("ix_clients_reminder_at", "clients", ["reminder_at"])


def downgrade() -> None:
    op.drop_index("ix_clients_reminder_at", table_name="clients")
    op.drop_index("ix_clients_status", table_name="clients")
    op.drop_index("ix_clients_team_id", table_name="clients")
    op.drop_index("ix_clients_manager_id", table_name="clients")
    op.drop_table("clients")

    op.drop_constraint("fk_users_team_id", "users", type_="foreignkey")
    op.drop_column("users", "team_id")
    op.drop_column("users", "role")

    op.drop_index("ix_teams_invite_code", table_name="teams")
    op.drop_table("teams")
