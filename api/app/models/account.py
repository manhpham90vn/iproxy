import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class UserRole(str, enum.Enum):
    admin = "admin"


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(256), nullable=False)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.admin)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class AccountStatus(str, enum.Enum):
    active = "active"
    disabled = "disabled"
    error = "error"
    forbidden = "forbidden"


class AccountTier(str, enum.Enum):
    free = "free"
    pro = "pro"
    ultra = "ultra"


class GoogleAccount(Base):
    __tablename__ = "google_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(256), unique=True, nullable=False)
    name: Mapped[str | None] = mapped_column(String(256))
    label: Mapped[str | None] = mapped_column(String(128))
    custom_label: Mapped[str | None] = mapped_column(String(128))
    tier: Mapped[AccountTier] = mapped_column(Enum(AccountTier), default=AccountTier.free)
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), default=AccountStatus.active)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, default=0)

    # OAuth tokens
    refresh_token: Mapped[str | None] = mapped_column(Text)
    access_token: Mapped[str | None] = mapped_column(Text)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime)

    # Proxy
    proxy_id: Mapped[int | None] = mapped_column(ForeignKey("proxy_pool.id"), nullable=True)
    proxy_disabled: Mapped[bool] = mapped_column(Boolean, default=False)
    proxy_disabled_reason: Mapped[str | None] = mapped_column(Text)
    proxy_disabled_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Disabled state
    disabled_reason: Mapped[str | None] = mapped_column(Text)
    disabled_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Validation blocking
    validation_blocked: Mapped[bool] = mapped_column(Boolean, default=False)
    validation_blocked_until: Mapped[datetime | None] = mapped_column(DateTime)
    validation_blocked_reason: Mapped[str | None] = mapped_column(Text)
    validation_url: Mapped[str | None] = mapped_column(Text)

    # Protected models (JSON array)
    protected_models: Mapped[str | None] = mapped_column(Text)

    # Quota (JSON blob)
    quota_data: Mapped[str | None] = mapped_column(Text)
    quota_updated_at: Mapped[datetime | None] = mapped_column(DateTime)

    # Timestamps
    last_used: Mapped[datetime | None] = mapped_column(DateTime)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    fingerprint: Mapped["DeviceFingerprint | None"] = relationship(
        back_populates="account", uselist=False, cascade="all, delete-orphan"
    )
    fingerprint_versions: Mapped[list["DeviceFingerprintVersion"]] = relationship(
        back_populates="account", cascade="all, delete-orphan"
    )
    proxy: Mapped["ProxyPool | None"] = relationship(back_populates="accounts")  # noqa: F821


class DeviceFingerprint(Base):
    __tablename__ = "device_fingerprints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("google_accounts.id"), unique=True)
    machine_id: Mapped[str | None] = mapped_column(String(256))
    mac_machine_id: Mapped[str | None] = mapped_column(String(256))
    dev_device_id: Mapped[str | None] = mapped_column(String(256))
    sqm_id: Mapped[str | None] = mapped_column(String(256))
    user_agent: Mapped[str | None] = mapped_column(Text)
    accept_language: Mapped[str | None] = mapped_column(String(256))
    platform: Mapped[str | None] = mapped_column(String(64))
    data: Mapped[str | None] = mapped_column(Text)  # JSON blob for extra fields
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    account: Mapped["GoogleAccount"] = relationship(back_populates="fingerprint")


class DeviceFingerprintVersion(Base):
    __tablename__ = "device_fingerprint_versions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("google_accounts.id"))
    label: Mapped[str | None] = mapped_column(String(128))
    machine_id: Mapped[str | None] = mapped_column(String(256))
    mac_machine_id: Mapped[str | None] = mapped_column(String(256))
    dev_device_id: Mapped[str | None] = mapped_column(String(256))
    sqm_id: Mapped[str | None] = mapped_column(String(256))
    data: Mapped[str | None] = mapped_column(Text)
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    account: Mapped["GoogleAccount"] = relationship(back_populates="fingerprint_versions")
