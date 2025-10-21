"""Add tables

Revision ID: 8edd4c89e3b0
Revises:
Create Date: 2025-10-20 19:07:20.343445

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8edd4c89e3b0"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(sa.text('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"'))

    op.create_table(
        "event_types",
        sa.Column("id", sa.String(length=32), nullable=False),
        sa.Column("name", sa.String(length=32), nullable=False),
        sa.Column(
            "is_deletable", sa.Boolean(), nullable=False, server_default=sa.text("true")
        ),
        sa.Column("description", sa.String(length=255), nullable=False),
        sa.Column(
            "created_time",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_time",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.bulk_insert(
        sa.table(
            "event_types",
            sa.column("id", sa.String(length=32)),
            sa.column("name", sa.String(length=32)),
            sa.column("description", sa.String(length=255)),
            sa.column("is_deletable", sa.Boolean()),
        ),
        [
            {
                "id": "vaccine_expirations",
                "name": "Vaccine expirations",
                "description": "Vaccine expirations including seasonal boosters",
                "is_deletable": False,
            },
            {
                "id": "upcoming_dental_procedures",
                "name": "Upcoming dental procedures",
                "description": "Upcoming dental procedures",
                "is_deletable": False,
            },
            {
                "id": "routine_exams",
                "name": "Routine exams",
                "description": "Routine exams",
                "is_deletable": False,
            },
            {
                "id": "follow_up_appointments",
                "name": "Follow-up appointments",
                "description": "Follow-up appointments",
                "is_deletable": False,
            },
        ],
    )

    op.create_table(
        "medical_records",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("filename", sa.String(), nullable=False),
        sa.Column(
            "created_time",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_time",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "events",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("medical_record_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("event_type_id", sa.String(length=32), nullable=False),
        sa.Column("event", sa.String(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column(
            "created_time",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated_time",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.ForeignKeyConstraint(
            ["event_type_id"], ["event_types.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["medical_record_id"], ["medical_records.id"], ondelete="CASCADE"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_events_event_type_id"), "events", ["event_type_id"], unique=False
    )
    op.create_index(
        op.f("ix_events_medical_record_id"),
        "events",
        ["medical_record_id"],
        unique=False,
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_events_medical_record_id"), table_name="events")
    op.drop_index(op.f("ix_events_event_type_id"), table_name="events")
    op.drop_table("events")
    op.drop_table("medical_records")
    op.drop_table("event_types")
