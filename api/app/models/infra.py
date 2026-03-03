import enum
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ProxyProtocol(str, enum.Enum):
    http = "http"
    https = "https"
    socks5 = "socks5"


class ProxyPool(Base):
    __tablename__ = "proxy_pool"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    host: Mapped[str] = mapped_column(String(256), nullable=False)
    port: Mapped[int] = mapped_column(Integer, nullable=False)
    protocol: Mapped[ProxyProtocol] = mapped_column(Enum(ProxyProtocol), default=ProxyProtocol.http)
    username: Mapped[str | None] = mapped_column(String(128))
    password: Mapped[str | None] = mapped_column(String(256))
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    latency_ms: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    accounts: Mapped[list["GoogleAccount"]] = relationship(back_populates="proxy")  # noqa: F821


class IpWhitelist(Base):
    __tablename__ = "ip_whitelist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cidr: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    note: Mapped[str | None] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class IpBlacklist(Base):
    __tablename__ = "ip_blacklist"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    cidr: Mapped[str] = mapped_column(String(64), unique=True, nullable=False)
    note: Mapped[str | None] = mapped_column(String(256))
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class TokenUsage(Base):
    __tablename__ = "token_usage"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    model: Mapped[str] = mapped_column(String(128), nullable=False)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    recorded_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class RequestLog(Base):
    __tablename__ = "request_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    account_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    api_key_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    method: Mapped[str] = mapped_column(String(16))
    path: Mapped[str] = mapped_column(String(512))
    status_code: Mapped[int | None] = mapped_column(Integer)
    client_ip: Mapped[str | None] = mapped_column(String(64))
    duration_ms: Mapped[int | None] = mapped_column(Integer)
    error: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
