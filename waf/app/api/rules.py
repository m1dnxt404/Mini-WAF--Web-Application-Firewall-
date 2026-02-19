from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.models import WafRule

router = APIRouter(prefix="/api", tags=["rules"])


def _serialize_rule(rule: WafRule) -> dict:
    return {
        "id": rule.id,
        "name": rule.name,
        "type": rule.type,
        "pattern": rule.pattern,
        "score": rule.score,
        "action": rule.action,
        "enabled": rule.enabled,
        "created_at": rule.created_at.isoformat() if rule.created_at else None,
    }


@router.get("/rules")
async def list_rules(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WafRule).order_by(WafRule.created_at))
    rules = result.scalars().all()
    return [_serialize_rule(rule) for rule in rules]


@router.patch("/rules/{rule_id}/toggle")
async def toggle_rule(rule_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WafRule).where(WafRule.id == rule_id))
    rule = result.scalar_one_or_none()
    if rule is None:
        raise HTTPException(status_code=404, detail="Rule not found")

    rule.enabled = not rule.enabled
    await db.commit()
    await db.refresh(rule)
    return _serialize_rule(rule)
