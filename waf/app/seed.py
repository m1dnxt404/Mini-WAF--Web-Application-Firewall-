"""Seed default WAF rules on first startup."""

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import WafRule

# These rules cover the most common web attack vectors.
# Each pattern is matched case-insensitively against: method + path + query + body.
_DEFAULT_RULES: list[dict] = [
    # ── SQL Injection ─────────────────────────────────────────────────────────
    {
        "name": "SQLi – UNION SELECT",
        "type": "SQLi",
        "pattern": r"union\s+(all\s+)?select",
        "score": 60,
        "action": "block",
    },
    {
        "name": "SQLi – Tautology (OR 1=1)",
        "type": "SQLi",
        "pattern": r"\b(or|and)\b\s+[\w'\"]+\s*=\s*[\w'\"]+",
        "score": 40,
        "action": "block",
    },
    {
        "name": "SQLi – Inline Comment",
        "type": "SQLi",
        "pattern": r"(--|#|/\*|\*/)",
        "score": 20,
        "action": "log",
    },
    {
        "name": "SQLi – Stacked Queries",
        "type": "SQLi",
        "pattern": r";\s*(select|insert|update|delete|drop|exec)",
        "score": 60,
        "action": "block",
    },
    # ── Cross-Site Scripting ──────────────────────────────────────────────────
    {
        "name": "XSS – Script Tag",
        "type": "XSS",
        "pattern": r"<\s*script[^>]*>",
        "score": 60,
        "action": "block",
    },
    {
        "name": "XSS – Inline Event Handler",
        "type": "XSS",
        "pattern": r"\bon(load|error|click|mouseover|focus|blur|submit|keydown|keyup)\s*=",
        "score": 50,
        "action": "block",
    },
    {
        "name": "XSS – javascript: Protocol",
        "type": "XSS",
        "pattern": r"javascript\s*:",
        "score": 50,
        "action": "block",
    },
    # ── Path Traversal ────────────────────────────────────────────────────────
    {
        "name": "Path Traversal – Dot-Dot Slash",
        "type": "PathTraversal",
        "pattern": r"(\.\./|\.\.\\|%2e%2e%2f|%2e%2e%5c|\.\.%2f|\.\.%5c)",
        "score": 50,
        "action": "block",
    },
    {
        "name": "Path Traversal – Sensitive Files",
        "type": "PathTraversal",
        "pattern": r"(etc/passwd|etc/shadow|proc/self|win\.ini|system32)",
        "score": 70,
        "action": "block",
    },
    # ── Command Injection ─────────────────────────────────────────────────────
    {
        "name": "CmdInjection – Shell Metacharacters",
        "type": "CmdInjection",
        "pattern": r"[;&|`$]\s*(ls|cat|id|whoami|uname|curl|wget|bash|sh|cmd|powershell)",
        "score": 70,
        "action": "block",
    },
    {
        "name": "CmdInjection – Subshell",
        "type": "CmdInjection",
        "pattern": r"(\$\(|\`)[^)]*[)|\`]",
        "score": 60,
        "action": "block",
    },
    # ── SSRF ──────────────────────────────────────────────────────────────────
    {
        "name": "SSRF – Internal Address",
        "type": "SSRF",
        "pattern": (
            r"(https?://)?(localhost|127\.0\.0\.1|0\.0\.0\.0|169\.254\.|"
            r"10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+|192\.168\.)"
        ),
        "score": 40,
        "action": "log",
    },
]


async def seed_default_rules(db: AsyncSession) -> None:
    """Insert default rules if the waf_rules table is empty."""
    count = (await db.execute(select(func.count()).select_from(WafRule))).scalar() or 0
    if count > 0:
        return

    for r in _DEFAULT_RULES:
        db.add(
            WafRule(
                name=r["name"],
                type=r["type"],
                pattern=r["pattern"],
                score=r["score"],
                action=r["action"],
                enabled=True,
            )
        )
    await db.commit()
