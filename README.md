# Mini WAF — Web Application Firewall

A containerized, rule-based reverse-proxy Web Application Firewall built with
FastAPI, PostgreSQL, and Redis. Inspects incoming HTTP traffic, applies threat
scoring, rate limiting, and configurable detection rules before forwarding
requests to the backend.

---

## Architecture

```text
Client → NGINX (port 80) → WAF Service (port 8000) → Backend API (port 8001)
                                    ↓
                           PostgreSQL + Redis
```

The WAF sits as a **dedicated proxy layer** between NGINX and the backend.
Every request is inspected, scored, and logged before being forwarded.

---

## Tech Stack

| Layer          | Technology                              |
|----------------|-----------------------------------------|
| WAF Engine     | FastAPI + Uvicorn (Python 3.11)         |
| Reverse Proxy  | NGINX                                   |
| Database       | PostgreSQL 15 (attack logs, rules, IPs) |
| Cache          | Redis 7 (rate limiting, threat cache)   |
| ORM            | SQLAlchemy 2.0 (async)                  |
| Migrations     | Alembic                                 |
| Config         | pydantic-settings                       |
| Infrastructure | Docker + Docker Compose                 |
| Dashboard      | React + Tailwind + Recharts (Week 2)    |

---

## Project Structure

```text
mini-waf/
├── waf/                        # WAF engine service
│   ├── app/
│   │   ├── main.py             # FastAPI app, lifespan, health endpoints
│   │   ├── core/
│   │   │   ├── config.py       # Settings via pydantic-settings
│   │   │   └── database.py     # Async SQLAlchemy engine + session
│   │   └── models/
│   │       └── models.py       # ORM models (4 tables)
│   ├── alembic/                # Database migrations
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
├── backend/                    # Dummy target backend API
│   ├── app/main.py
│   ├── requirements.txt
│   └── Dockerfile
├── nginx/
│   └── nginx.conf              # Routes port 80 → WAF
├── docker-compose.yml
├── .env                        # Local secrets (not committed)
└── .env.example                # Template for environment variables
```

---

## Quick Start

### Prerequisites

- [Docker Desktop](https://www.docker.com/products/docker-desktop/)
- [Docker Compose](https://docs.docker.com/compose/) (included with Docker Desktop)

### 1. Clone and configure environment

```bash
git clone <repo-url>
cd mini-waf
cp .env.example .env
```

Edit `.env` if you want to change default credentials (optional for local dev).

### 2. Start all services

```bash
docker compose up --build -d
```

### 3. Verify everything is running

```bash
docker compose ps
```

```text
NAME        STATUS                  PORTS
postgres    Up (healthy)            5432/tcp
redis       Up (healthy)            6379/tcp
waf         Up                      0.0.0.0:8000->8000/tcp
backend     Up                      0.0.0.0:8001->8001/tcp
nginx       Up                      0.0.0.0:80->80/tcp
```

### 4. Check health

```bash
curl http://localhost/health
# {"status": "ok", "service": "mini-waf"}

curl http://localhost/ready
# {"db": "ok", "redis": "ok"}
```

---

## API Endpoints (Day 1)

| Method | Path      | Description                         |
|--------|-----------|-------------------------------------|
| GET    | `/health` | Service liveness check              |
| GET    | `/ready`  | Readiness check (DB + Redis status) |

> More endpoints will be added in subsequent days per the build roadmap.

---

## Database Schema

Four PostgreSQL tables are auto-created on WAF startup via SQLAlchemy:

| Table            | Purpose                                      |
|------------------|----------------------------------------------|
| `attack_logs`    | Every inspected request with threat score    |
| `waf_rules`      | Configurable regex-based detection rules     |
| `blocked_ips`    | Permanently blocked IPs with optional expiry |
| `ip_rate_limits` | Per-IP sliding window request counters       |

---

## Environment Variables

| Variable                 | Default                                              | Description                  |
|--------------------------|------------------------------------------------------|------------------------------|
| `DATABASE_URL`           | `postgresql+asyncpg://waf_user:waf_password@...`     | Async PostgreSQL URL         |
| `REDIS_URL`              | `redis://redis:6379/0`                               | Redis connection URL         |
| `BACKEND_URL`            | `http://backend:8001`                                | Target backend URL           |
| `THREAT_SCORE_THRESHOLD` | `50`                                                 | Score to trigger a block     |
| `PGADMIN_EMAIL`          | `admin@waf.local`                                    | pgAdmin4 login email         |
| `PGADMIN_PASSWORD`       | `admin_password`                                     | pgAdmin4 login password      |

---

## pgAdmin4 (DB GUI)

> See [Setup_docker_Redis.md](Setup_docker_Redis.md) for full setup instructions.

Add `pgadmin` service to `docker-compose.yml`, then access at:
[http://localhost:5050](http://localhost:5050)

Connection settings:
- Host: `postgres`
- Port: `5432`
- Database: `waf_db`
- Username: `waf_user`

---

## Build Roadmap

### Week 1 — Core WAF Engine

| Days  | Task                                               | Status      |
|-------|----------------------------------------------------|-------------|
| 1–2   | Project setup, Docker, PostgreSQL, Redis, FastAPI  | ✅ Done      |
| 3–4   | Reverse proxy — forward requests, capture metadata | ⬜ Pending  |
| 5     | Rule Engine — load JSON rules, regex matching      | ⬜ Pending  |
| 6–7   | Threat Scoring Engine + PostgreSQL logging         | ⬜ Pending  |

### Week 2 — Protection Features

| Days  | Task                                               | Status      |
|-------|----------------------------------------------------|-------------|
| 8–9   | Redis rate limiting (sliding window)               | ⬜ Pending  |
| 10    | Persistent IP blacklist + auto-block               | ⬜ Pending  |
| 11–12 | Admin API (rules, IPs, threshold management)       | ⬜ Pending  |
| 13–14 | React dashboard with real-time WebSocket logs      | ⬜ Pending  |

### Week 3 — Advanced (Optional)

- GeoIP blocking
- Bot detection heuristics
- JWT / API key validation
- CI/CD pipeline + cloud deployment
- Prometheus + Grafana monitoring

---

## Useful Commands

```bash
# View WAF logs
docker compose logs -f waf

# Open psql shell
docker compose exec postgres psql -U waf_user -d waf_db

# Open Redis CLI
docker compose exec redis redis-cli

# Rebuild WAF after code changes
docker compose up --build waf -d

# Stop all services
docker compose down

# Stop and wipe all data
docker compose down -v
```

---

## Detection Capabilities (Planned)

- SQL Injection (SQLi)
- Cross-Site Scripting (XSS)
- Path Traversal
- Command Injection
- Suspicious Headers
- Bot Signatures
- Brute-force / DoS via rate limiting
