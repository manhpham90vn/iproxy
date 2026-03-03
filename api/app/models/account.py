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
    tier: Mapped[AccountTier] = mapped_column(Enum(AccountTier), default=AccountTier.free)
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), default=AccountStatus.active)
    refresh_token: Mapped[str | None] = mapped_column(Text)
    access_token: Mapped[str | None] = mapped_column(Text)
    token_expiry: Mapped[datetime | None] = mapped_column(DateTime)
    proxy_id: Mapped[int | None] = mapped_column(ForeignKey("proxy_pool.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    fingerprint: Mapped["DeviceFingerprint | None"] = relationship(back_populates="account", uselist=False)
    proxy: Mapped["ProxyPool | None"] = relationship(back_populates="accounts")  # noqa: F821


class DeviceFingerprint(Base):
    __tablename__ = "device_fingerprints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int] = mapped_column(ForeignKey("google_accounts.id"), unique=True)
    user_agent: Mapped[str | None] = mapped_column(Text)
    accept_language: Mapped[str | None] = mapped_column(String(256))
    platform: Mapped[str | None] = mapped_column(String(64))
    data: Mapped[str | None] = mapped_column(Text)  # JSON blob
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())

    account: Mapped["GoogleAccount"] = relationship(back_populates="fingerprint")
