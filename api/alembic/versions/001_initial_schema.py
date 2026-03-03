"""initial schema

Revision ID: 001
Revises:
Create Date: 2026-03-03

"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("username", sa.String(64), nullable=False, unique=True),
        sa.Column("hashed_password", sa.String(256), nullable=False),
        sa.Column("role", sa.Enum("admin", name="userrole"), nullable=False, server_default="admin"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "proxy_pool",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("host", sa.String(256), nullable=False),
        sa.Column("port", sa.Integer(), nullable=False),
        sa.Column(
            "protocol", sa.Enum("http", "https", "socks5", name="proxyprotocol"), nullable=False, server_default="http"
        ),
        sa.Column("username", sa.String(128)),
        sa.Column("password", sa.String(256)),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("latency_ms", sa.Integer()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "google_accounts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(256), nullable=False, unique=True),
        sa.Column("name", sa.String(256)),
        sa.Column("label", sa.String(128)),
        sa.Column("tier", sa.Enum("free", "pro", "ultra", name="accounttier"), nullable=False, server_default="free"),
        sa.Column(
            "status",
            sa.Enum("active", "disabled", "error", name="accountstatus"),
            nullable=False,
            server_default="active",
        ),
        sa.Column("refresh_token", sa.Text()),
        sa.Column("access_token", sa.Text()),
        sa.Column("token_expiry", sa.DateTime()),
        sa.Column("proxy_id", sa.Integer(), sa.ForeignKey("proxy_pool.id"), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "device_fingerprints",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer(), sa.ForeignKey("google_accounts.id"), unique=True),
        sa.Column("user_agent", sa.Text()),
        sa.Column("accept_language", sa.String(256)),
        sa.Column("platform", sa.String(64)),
        sa.Column("data", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "api_keys",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(128), nullable=False),
        sa.Column("key", sa.String(256), nullable=False, unique=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("expires_at", sa.DateTime()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "ip_whitelist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cidr", sa.String(64), nullable=False, unique=True),
        sa.Column("note", sa.String(256)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "ip_blacklist",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cidr", sa.String(64), nullable=False, unique=True),
        sa.Column("note", sa.String(256)),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "token_usage",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer()),
        sa.Column("model", sa.String(128), nullable=False),
        sa.Column("input_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("output_tokens", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("recorded_at", sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_table(
        "request_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("account_id", sa.Integer()),
        sa.Column("api_key_id", sa.Integer()),
        sa.Column("method", sa.String(16)),
        sa.Column("path", sa.String(512)),
        sa.Column("status_code", sa.Integer()),
        sa.Column("client_ip", sa.String(64)),
        sa.Column("duration_ms", sa.Integer()),
        sa.Column("error", sa.Text()),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("request_logs")
    op.drop_table("token_usage")
    op.drop_table("ip_blacklist")
    op.drop_table("ip_whitelist")
    op.drop_table("api_keys")
    op.drop_table("device_fingerprints")
    op.drop_table("google_accounts")
    op.drop_table("proxy_pool")
    op.drop_table("users")
    op.execute("DROP TYPE IF EXISTS userrole")
    op.execute("DROP TYPE IF EXISTS accounttier")
    op.execute("DROP TYPE IF EXISTS accountstatus")
    op.execute("DROP TYPE IF EXISTS proxyprotocol")
