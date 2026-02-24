import json
from contextlib import asynccontextmanager

import httpx
import redis.asyncio as aioredis
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, Response
from sqlalchemy import select, text

from app.api import blocked_ips, logs, rules
from app.api.ws import manager
from app.core.config import settings
from app.core.database import AsyncSessionLocal, init_db
from app.engine import inspect_request
from app.models.models import AttackLog, BlockedIP
from app.seed import seed_default_rules

# Headers that must not be forwarded between proxies (RFC 7230 §6.1).
_HOP_BY_HOP = frozenset(
    {
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "transfer-encoding",
        "upgrade",
    }
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ── Startup ──────────────────────────────────────────────────────────────
    await init_db()

    async with AsyncSessionLocal() as db:
        await seed_default_rules(db)

    app.state.redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )

    # Shared httpx client — reuses connection pool across requests.
    app.state.http_client = httpx.AsyncClient(
        timeout=httpx.Timeout(30.0),
        follow_redirects=True,
    )

    yield

    # ── Shutdown ─────────────────────────────────────────────────────────────
    await app.state.redis.aclose()
    await app.state.http_client.aclose()


app = FastAPI(
    title="Mini WAF",
    description="A rule-based reverse-proxy Web Application Firewall",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(logs.router)
app.include_router(rules.router)
app.include_router(blocked_ips.router)


@app.get("/health")
async def health():
    return {"status": "ok", "service": "mini-waf"}


@app.get("/ready")
async def ready():
    db_status = "ok"
    redis_status = "ok"

    try:
        async with AsyncSessionLocal() as session:
            await session.execute(text("SELECT 1"))
    except Exception:
        db_status = "error"

    try:
        await app.state.redis.ping()
    except Exception:
        redis_status = "error"

    status_code = 200 if db_status == "ok" and redis_status == "ok" else 503
    return JSONResponse(
        content={"db": db_status, "redis": redis_status},
        status_code=status_code,
    )


@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive; WAF engine pushes via manager.broadcast()
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)


# ── Helpers ───────────────────────────────────────────────────────────────────


async def _write_log(
    ip: str,
    method: str,
    endpoint: str,
    headers: dict,
    body: str | None,
    threat_score: int,
    threat_types: list[str],
    action: str,
) -> AttackLog:
    """Persist an AttackLog row and broadcast it to all WS clients."""
    log = AttackLog(
        ip_address=ip,
        method=method,
        endpoint=endpoint,
        headers=headers,
        request_body=body,
        threat_score=threat_score,
        action_taken=action,
        threat_types=threat_types,
    )
    async with AsyncSessionLocal() as db:
        db.add(log)
        await db.commit()
        await db.refresh(log)

    await manager.broadcast(
        json.dumps(
            {
                "type": "new_log",
                "data": {
                    "id": log.id,
                    "ip_address": log.ip_address,
                    "method": log.method,
                    "endpoint": log.endpoint,
                    "threat_score": log.threat_score,
                    "action_taken": log.action_taken,
                    "threat_types": log.threat_types or [],
                    "created_at": log.created_at.isoformat(),
                },
            }
        )
    )
    return log


# ── Reverse proxy catch-all ───────────────────────────────────────────────────
# Registered LAST so that all specific WAF routes (/health, /ready, /api/*, /ws/*)
# are matched first by FastAPI's router before falling through here.


@app.api_route(
    "/{path:path}",
    methods=["GET", "POST", "PUT", "PATCH", "DELETE", "HEAD", "OPTIONS"],
    include_in_schema=False,
)
async def reverse_proxy(request: Request, path: str):
    full_path = f"/{path}"
    ip: str = request.headers.get("X-Real-IP") or (
        request.client.host if request.client else "unknown"
    )
    body_bytes: bytes = await request.body()
    body_str: str | None = body_bytes.decode("utf-8", errors="replace") if body_bytes else None
    query: str = request.url.query

    redis = request.app.state.redis
    http_client: httpx.AsyncClient = request.app.state.http_client

    # ── 1. Redis temporary block check ────────────────────────────────────────
    if await redis.get(f"blocked:{ip}"):
        await _write_log(
            ip, request.method, full_path, dict(request.headers),
            body_str, 100, ["IP_BLOCKED"], "block",
        )
        return JSONResponse(status_code=403, content={"detail": "Your IP has been blocked."})

    # ── 2. DB permanent block + WAF rule inspection (single DB session) ───────
    async with AsyncSessionLocal() as db:
        blocked = (
            await db.execute(select(BlockedIP).where(BlockedIP.ip_address == ip))
        ).scalar_one_or_none()

        if blocked:
            await _write_log(
                ip, request.method, full_path, dict(request.headers),
                body_str, 100, ["IP_BLOCKED"], "block",
            )
            return JSONResponse(status_code=403, content={"detail": "Your IP has been blocked."})

        threat_score, threat_types, action = await inspect_request(
            db, request.method, full_path, query, body_str
        )

    # ── 3. Log every request (allowed and blocked alike) ─────────────────────
    await _write_log(
        ip, request.method, full_path, dict(request.headers),
        body_str, threat_score, threat_types, action,
    )

    # ── 4. Enforce block decision ─────────────────────────────────────────────
    if action == "block":
        return JSONResponse(
            status_code=403,
            content={"detail": "Request blocked by WAF", "threat_types": threat_types},
        )

    # ── 5. Forward allowed request to backend ─────────────────────────────────
    backend_url = settings.BACKEND_URL.rstrip("/") + full_path
    if query:
        backend_url += f"?{query}"

    forward_headers = {
        k: v
        for k, v in request.headers.items()
        if k.lower() not in _HOP_BY_HOP and k.lower() != "host"
    }
    forward_headers["X-Forwarded-For"] = ip
    forward_headers["X-Real-IP"] = ip
    forward_headers["X-Forwarded-Host"] = request.headers.get("host", "")

    try:
        backend_resp = await http_client.request(
            method=request.method,
            url=backend_url,
            headers=forward_headers,
            content=body_bytes,
        )
    except httpx.RequestError as exc:
        return JSONResponse(status_code=502, content={"detail": f"Backend unreachable: {exc!s}"})

    # Strip hop-by-hop and encoding headers from the backend response so the
    # client receives raw content (httpx already decompresses the body).
    excluded_resp = _HOP_BY_HOP | {"content-encoding", "content-length"}
    resp_headers = {
        k: v for k, v in backend_resp.headers.items() if k.lower() not in excluded_resp
    }

    return Response(
        content=backend_resp.content,
        status_code=backend_resp.status_code,
        headers=resp_headers,
    )
