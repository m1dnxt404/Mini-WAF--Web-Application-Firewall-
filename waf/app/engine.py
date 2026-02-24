"""WAF inspection engine — scores an incoming request against enabled rules."""

import re

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.models import WafRule


async def inspect_request(
    db: AsyncSession,
    method: str,
    path: str,
    query: str,
    body: str | None,
) -> tuple[int, list[str], str]:
    """Score the request against all enabled WAF rules.

    Returns:
        (threat_score, threat_types, action_taken)
        action_taken is "block" when score >= THREAT_SCORE_THRESHOLD, else "allow".
    """
    result = await db.execute(select(WafRule).where(WafRule.enabled == True))  # noqa: E712
    rules = result.scalars().all()

    # Build inspection corpus: method + path + query string + body.
    # We intentionally skip header values here to avoid false positives
    # (e.g. Content-Type containing HTML keywords). Header inspection can
    # be added as a separate rule category later.
    parts = [method, path]
    if query:
        parts.append(query)
    if body:
        parts.append(body)
    target = "\n".join(parts)

    total_score = 0
    # Use a dict to deduplicate threat types while preserving first-seen order.
    matched: dict[str, bool] = {}

    for rule in rules:
        try:
            if re.search(rule.pattern, target, re.IGNORECASE):
                total_score += rule.score
                matched[rule.type] = True
        except re.error:
            # Skip malformed patterns silently — don't crash the proxy.
            continue

    threat_types = list(matched.keys())
    action = "block" if total_score >= settings.THREAT_SCORE_THRESHOLD else "allow"
    return total_score, threat_types, action
