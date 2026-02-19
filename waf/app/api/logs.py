import json
from datetime import datetime, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import AttackLog

router = APIRouter(prefix="/api", tags=["logs"])


def _serialize_log(log: AttackLog) -> dict:
    return {
        "id": log.id,
        "ip_address": log.ip_address,
        "method": log.method,
        "endpoint": log.endpoint,
        "threat_score": log.threat_score,
        "action_taken": log.action_taken,
        "threat_types": log.threat_types or [],
        "created_at": log.created_at.isoformat() if log.created_at else None,
    }


@router.get("/logs")
async def list_logs(
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AttackLog).order_by(desc(AttackLog.created_at)).limit(limit).offset(offset)
    )
    logs = result.scalars().all()
    return [_serialize_log(log) for log in logs]


@router.get("/stats")
async def get_stats(db: AsyncSession = Depends(get_db)):
    total_result = await db.execute(select(func.count()).select_from(AttackLog))
    total = total_result.scalar() or 0

    blocked_result = await db.execute(
        select(func.count()).select_from(AttackLog).where(AttackLog.action_taken == "block")
    )
    blocked = blocked_result.scalar() or 0

    allowed_result = await db.execute(
        select(func.count()).select_from(AttackLog).where(AttackLog.action_taken == "allow")
    )
    allowed = allowed_result.scalar() or 0

    # Top 5 attacking IPs
    top_ips_result = await db.execute(
        select(AttackLog.ip_address, func.count().label("count"))
        .group_by(AttackLog.ip_address)
        .order_by(desc("count"))
        .limit(5)
    )
    top_ips = [{"ip": row.ip_address, "count": row.count} for row in top_ips_result]

    # Threat type distribution (unnest TEXT[] column)
    threat_rows = await db.execute(
        select(AttackLog.threat_types).where(AttackLog.threat_types.isnot(None))
    )
    threat_counter: dict[str, int] = {}
    for row in threat_rows:
        for t in (row.threat_types or []):
            threat_counter[t] = threat_counter.get(t, 0) + 1
    threat_distribution = [{"type": k, "count": v} for k, v in threat_counter.items()]

    # Requests per hour over last 24 hours
    since = datetime.utcnow() - timedelta(hours=24)
    hourly_result = await db.execute(
        select(
            func.date_trunc("hour", AttackLog.created_at).label("hour"),
            func.count().label("count"),
        )
        .where(AttackLog.created_at >= since)
        .group_by("hour")
        .order_by("hour")
    )
    requests_over_time = [
        {"hour": row.hour.strftime("%H:%M") if row.hour else "", "count": row.count}
        for row in hourly_result
    ]

    return {
        "total_requests": total,
        "blocked_requests": blocked,
        "allowed_requests": allowed,
        "top_ips": top_ips,
        "threat_distribution": threat_distribution,
        "requests_over_time": requests_over_time,
    }
