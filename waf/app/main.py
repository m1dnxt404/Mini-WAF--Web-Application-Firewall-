from contextlib import asynccontextmanager

import redis.asyncio as aioredis
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.api import blocked_ips, logs, rules
from app.api.ws import manager
from app.core.config import settings
from app.core.database import AsyncSessionLocal, init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_db()

    app.state.redis = aioredis.from_url(
        settings.REDIS_URL,
        encoding="utf-8",
        decode_responses=True,
    )

    yield

    # Shutdown
    await app.state.redis.aclose()


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
            # Keep connection alive; WAF engine will push via manager.broadcast()
            await websocket.receive_text()
    except WebSocketDisconnect:
        manager.disconnect(websocket)
