from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import BlockedIP

router = APIRouter(prefix="/api", tags=["blocked-ips"])


def _serialize_ip(ip: BlockedIP) -> dict:
    return {
        "id": ip.id,
        "ip_address": ip.ip_address,
        "reason": ip.reason,
        "expires_at": ip.expires_at.isoformat() if ip.expires_at else None,
        "created_at": ip.created_at.isoformat() if ip.created_at else None,
    }


@router.get("/blocked-ips")
async def list_blocked_ips(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BlockedIP).order_by(BlockedIP.created_at.desc()))
    ips = result.scalars().all()
    return [_serialize_ip(ip) for ip in ips]


@router.delete("/blocked-ips/{ip_address}")
async def unblock_ip(ip_address: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(BlockedIP).where(BlockedIP.ip_address == ip_address))
    ip = result.scalar_one_or_none()
    if ip is None:
        raise HTTPException(status_code=404, detail="IP not found in blocklist")

    await db.execute(delete(BlockedIP).where(BlockedIP.ip_address == ip_address))
    await db.commit()
    return {"message": f"{ip_address} has been unblocked"}
