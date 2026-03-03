"""Add account fields

Revision ID: 002
Revises: 001
Create Date: 2026-03-04

"""

from typing import Sequence, Union

import sqlalchemy as sa

from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to google_accounts table
    op.add_column("google_accounts", sa.Column("custom_label", sa.String(128), nullable=True))
    op.add_column("google_accounts", sa.Column("is_current", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("google_accounts", sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"))
    op.add_column("google_accounts", sa.Column("proxy_disabled", sa.Boolean(), nullable=False, server_default="false"))
    op.add_column("google_accounts", sa.Column("proxy_disabled_reason", sa.Text(), nullable=True))
    op.add_column("google_accounts", sa.Column("proxy_disabled_at", sa.DateTime(), nullable=True))
    op.add_column("google_accounts", sa.Column("disabled_reason", sa.Text(), nullable=True))
    op.add_column("google_accounts", sa.Column("disabled_at", sa.DateTime(), nullable=True))
    op.add_column(
        "google_accounts", sa.Column("validation_blocked", sa.Boolean(), nullable=False, server_default="false")
    )
    op.add_column("google_accounts", sa.Column("validation_blocked_until", sa.DateTime(), nullable=True))
    op.add_column("google_accounts", sa.Column("validation_blocked_reason", sa.Text(), nullable=True))
    op.add_column("google_accounts", sa.Column("validation_url", sa.Text(), nullable=True))
    op.add_column("google_accounts", sa.Column("protected_models", sa.Text(), nullable=True))
    op.add_column("google_accounts", sa.Column("quota_data", sa.Text(), nullable=True))
    op.add_column("google_accounts", sa.Column("quota_updated_at", sa.DateTime(), nullable=True))
    op.add_column("google_accounts", sa.Column("last_used", sa.DateTime(), nullable=True))

    # Add machine_id columns to device_fingerprints
    op.add_column("device_fingerprints", sa.Column("machine_id", sa.String(256), nullable=True))
    op.add_column("device_fingerprints", sa.Column("mac_machine_id", sa.String(256), nullable=True))
    op.add_column("device_fingerprints", sa.Column("dev_device_id", sa.String(256), nullable=True))
    op.add_column("device_fingerprints", sa.Column("sqm_id", sa.String(256), nullable=True))

    # Create device_fingerprint_versions table
    op.create_table(
        "device_fingerprint_versions",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("google_accounts.id"), nullable=False),
        sa.Column("label", sa.String(128), nullable=True),
        sa.Column("machine_id", sa.String(256), nullable=True),
        sa.Column("mac_machine_id", sa.String(256), nullable=True),
        sa.Column("dev_device_id", sa.String(256), nullable=True),
        sa.Column("sqm_id", sa.String(256), nullable=True),
        sa.Column("data", sa.Text(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    # Add new status to accountstatus enum
    op.execute("ALTER TYPE accountstatus ADD VALUE IF NOT EXISTS 'forbidden'")


def downgrade() -> None:
    op.drop_table("device_fingerprint_versions")
    op.drop_column("device_fingerprints", "sqm_id")
    op.drop_column("device_fingerprints", "dev_device_id")
    op.drop_column("device_fingerprints", "mac_machine_id")
    op.drop_column("device_fingerprints", "machine_id")
    op.drop_column("google_accounts", "last_used")
    op.drop_column("google_accounts", "quota_updated_at")
    op.drop_column("google_accounts", "quota_data")
    op.drop_column("google_accounts", "protected_models")
    op.drop_column("google_accounts", "validation_url")
    op.drop_column("google_accounts", "validation_blocked_reason")
    op.drop_column("google_accounts", "validation_blocked_until")
    op.drop_column("google_accounts", "validation_blocked")
    op.drop_column("google_accounts", "disabled_at")
    op.drop_column("google_accounts", "disabled_reason")
    op.drop_column("google_accounts", "proxy_disabled_at")
    op.drop_column("google_accounts", "proxy_disabled_reason")
    op.drop_column("google_accounts", "proxy_disabled")
    op.drop_column("google_accounts", "sort_order")
    op.drop_column("google_accounts", "is_current")
    op.drop_column("google_accounts", "custom_label")
