import uuid
from datetime import datetime

from sqlalchemy import ARRAY, Boolean, Integer, Text, Timestamp, VARCHAR
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class AttackLog(Base):
    __tablename__ = "attack_logs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    ip_address: Mapped[str] = mapped_column(VARCHAR(45), nullable=False)
    method: Mapped[str] = mapped_column(VARCHAR(10), nullable=False)
    endpoint: Mapped[str] = mapped_column(Text, nullable=False)
    headers: Mapped[dict] = mapped_column(JSONB, nullable=True)
    request_body: Mapped[str | None] = mapped_column(Text, nullable=True)
    threat_score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    action_taken: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    threat_types: Mapped[list[str] | None] = mapped_column(ARRAY(Text), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        Timestamp(timezone=True), default=datetime.utcnow, nullable=False
    )


class WafRule(Base):
    __tablename__ = "waf_rules"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    name: Mapped[str] = mapped_column(VARCHAR(255), nullable=False)
    type: Mapped[str] = mapped_column(VARCHAR(50), nullable=False)
    pattern: Mapped[str] = mapped_column(Text, nullable=False)
    score: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    action: Mapped[str] = mapped_column(VARCHAR(20), nullable=False)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        Timestamp(timezone=True), default=datetime.utcnow, nullable=False
    )


class BlockedIP(Base):
    __tablename__ = "blocked_ips"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    ip_address: Mapped[str] = mapped_column(VARCHAR(45), nullable=False, unique=True)
    reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    expires_at: Mapped[datetime | None] = mapped_column(Timestamp(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        Timestamp(timezone=True), default=datetime.utcnow, nullable=False
    )


class IPRateLimit(Base):
    __tablename__ = "ip_rate_limits"

    ip_address: Mapped[str] = mapped_column(VARCHAR(45), primary_key=True)
    request_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    window_start: Mapped[datetime] = mapped_column(
        Timestamp(timezone=True), default=datetime.utcnow, nullable=False
    )
