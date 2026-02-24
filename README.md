# Mini WAF — Web Application Firewall

A containerized, rule-based reverse-proxy Web Application Firewall built with
FastAPI, PostgreSQL, Redis, and a React admin dashboard. Inspects incoming HTTP
traffic, applies threat scoring, rate limiting, and configurable detection rules
before forwarding requests to the backend.

---

## Architecture

```text
Browser → Dashboard (port 3000)
               ↕ REST / WebSocket
Client → NGINX (port 80) → WAF (port 8000) → Backend API (port 8001)
                                    ↓
                          PostgreSQL + Redis
```

The WAF sits as a **dedicated proxy layer** between NGINX and the backend.
Every request is inspected, scored, and logged before forwarding.
The dashboard connects directly to the WAF API and WebSocket for real-time monitoring.

---

## Tech Stack

| Layer          | Technology                                      |
|----------------|-------------------------------------------------|
| WAF Engine     | FastAPI + Uvicorn (Python 3.11)                 |
| Reverse Proxy  | NGINX                                           |
| Database       | PostgreSQL 15 (attack logs, rules, IP data)     |
| Cache          | Redis 7 (rate limiting, threat score cache)     |
| ORM            | SQLAlchemy 2.0 (async + asyncpg)                |
| Migrations     | Alembic (async mode)                            |
| Config         | pydantic-settings                               |
| Dashboard      | React 18 + Vite + TypeScript + Tailwind CSS v3  |
| Charts         | Recharts (PieChart, AreaChart)                  |
| Real-time      | WebSocket (`/ws/logs`)                          |
| Infrastructure | Docker + Docker Compose                         |

---

## Project Structure

```text
mini-waf/
├── waf/                           # WAF engine service
│   ├── app/
│   │   ├── main.py                # FastAPI app, CORS, routers, WebSocket, proxy catch-all
│   │   ├── engine.py              # WAF inspection — regex rule matching + threat scoring
│   │   ├── seed.py                # Default WAF rules seeded on first startup
│   │   ├── core/
│   │   │   ├── config.py          # Settings via pydantic-settings
│   │   │   └── database.py        # Async SQLAlchemy engine + session
│   │   ├── api/
│   │   │   ├── logs.py            # GET /api/logs, GET /api/stats
│   │   │   ├── rules.py           # GET /api/rules, PATCH /api/rules/{id}/toggle
│   │   │   ├── blocked_ips.py     # GET /api/blocked-ips, DELETE /api/blocked-ips/{ip}
│   │   │   └── ws.py              # ConnectionManager (WebSocket broadcast)
│   │   └── models/
│   │       └── models.py          # ORM models (4 tables)
│   ├── alembic/                   # Database migrations
│   ├── alembic.ini
│   ├── requirements.txt
│   └── Dockerfile
├── dashboard/                     # React admin dashboard
│   ├── src/
│   │   ├── App.tsx                # BrowserRouter + layout shell
│   │   ├── main.tsx               # React entry point
│   │   ├── index.css              # Tailwind directives
│   │   ├── lib/api.ts             # Typed fetch wrappers for WAF endpoints
│   │   ├── hooks/useWebSocket.ts  # Auto-reconnecting WS, 100-entry cap, pause
│   │   ├── components/
│   │   │   ├── Sidebar.tsx        # Nav with active link highlighting
│   │   │   ├── StatCard.tsx       # Reusable metric card
│   │   │   ├── LogsTable.tsx      # Color-coded attack log rows
│   │   │   ├── ThreatPieChart.tsx # Recharts donut chart
│   │   │   └── TimelineChart.tsx  # Recharts area chart (requests/hour)
│   │   └── pages/
│   │       ├── Overview.tsx       # Stats + charts + top IPs, auto-refreshes 10s
│   │       ├── LiveLogs.tsx       # Real-time WS feed + Pause/Resume
│   │       ├── Rules.tsx          # Rule list with enable/disable toggles
│   │       └── BlockedIPs.tsx     # Blocked IP list with Unblock action
│   ├── nginx.conf                 # nginx server block (React Router fallback)
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── Dockerfile                 # Multi-stage: node:20 build → nginx:alpine serve
├── backend/                       # Dummy target backend API
│   ├── app/main.py
│   ├── requirements.txt
│   └── Dockerfile
├── nginx/
│   └── nginx.conf                 # Routes port 80 → WAF
├── docker-compose.yml             # 7 services
├── .env                           # Local secrets (not committed)
├── .env.example                   # Template for environment variables
└── Setup_docker_Redis.md          # PostgreSQL + pgAdmin4 + Redis setup guide
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
pgadmin     Up                      0.0.0.0:5050->80/tcp
waf         Up                      0.0.0.0:8000->8000/tcp
backend     Up                      0.0.0.0:8001->8001/tcp
dashboard   Up                      0.0.0.0:3000->80/tcp
nginx       Up                      0.0.0.0:80->80/tcp
```

### 4. Access the services

| Service           | URL                                                     |
|-------------------|---------------------------------------------------------|
| Dashboard         | [http://localhost:3000](http://localhost:3000)          |
| WAF API (Swagger) | [http://localhost:8000/docs](http://localhost:8000/docs)|
| pgAdmin4          | [http://localhost:5050](http://localhost:5050)          |
| NGINX → WAF       | [http://localhost](http://localhost)                    |

---

## WAF API Reference

### System

| Method | Path      | Description                          |
|--------|-----------|--------------------------------------|
| GET    | `/health` | Service liveness check               |
| GET    | `/ready`  | Readiness check (DB + Redis status)  |

### Attack Logs

| Method | Path         | Description                                           |
|--------|--------------|-------------------------------------------------------|
| GET    | `/api/logs`  | List attack logs, newest first (`limit`, `offset`)    |
| GET    | `/api/stats` | Totals, top IPs, threat distribution, hourly timeline |

### Rules

| Method | Path                        | Description                    |
|--------|-----------------------------|--------------------------------|
| GET    | `/api/rules`                | List all WAF rules             |
| PATCH  | `/api/rules/{id}/toggle`    | Enable / disable a rule        |

### Blocked IPs

| Method | Path                        | Description                    |
|--------|-----------------------------|--------------------------------|
| GET    | `/api/blocked-ips`          | List all blocked IPs           |
| DELETE | `/api/blocked-ips/{ip}`     | Unblock an IP address          |

### WebSocket

| Protocol | Path       | Description                                                    |
|----------|------------|----------------------------------------------------------------|
| WS       | `/ws/logs` | Push `{"type":"new_log","data":{...}}` on each new attack log  |

---

## Dashboard Pages

| Page         | Route           | Description                                          |
|--------------|-----------------|------------------------------------------------------|
| Overview     | `/`             | 4 stat cards, threat pie chart, timeline, top IPs    |
| Live Logs    | `/live-logs`    | Real-time WebSocket feed, color-coded rows, Pause    |
| Rules        | `/rules`        | Enable/disable rules with toggle switches            |
| Blocked IPs  | `/blocked-ips`  | View and unblock IPs from the blocklist              |

---

## Database Schema

Four PostgreSQL tables are auto-created on WAF startup via `init_db()`:

| Table            | Purpose                                      |
|------------------|----------------------------------------------|
| `attack_logs`    | Every inspected request with threat score    |
| `waf_rules`      | Configurable regex-based detection rules     |
| `blocked_ips`    | Permanently or temporarily blocked IPs       |
| `ip_rate_limits` | Per-IP sliding window request counters       |

---

## Environment Variables

| Variable                 | Default                                          | Description                     |
|--------------------------|--------------------------------------------------|---------------------------------|
| `DATABASE_URL`           | `postgresql+asyncpg://waf_user:...@postgres/...` | Async PostgreSQL connection URL |
| `REDIS_URL`              | `redis://redis:6379/0`                           | Redis connection URL            |
| `BACKEND_URL`            | `http://backend:8001`                            | Target backend service URL      |
| `THREAT_SCORE_THRESHOLD` | `50`                                             | Score ceiling before block      |
| `CORS_ORIGINS`           | `http://localhost:3000`                          | Allowed CORS origins (CSV)      |
| `PGADMIN_EMAIL`          | `admin@waf.local`                                | pgAdmin4 login email            |
| `PGADMIN_PASSWORD`       | `admin_password`                                 | pgAdmin4 login password         |

---

## pgAdmin4 (DB GUI)

> See [Setup_docker_Redis.md](Setup_docker_Redis.md) for full setup instructions.

Access at [http://localhost:5050](http://localhost:5050) — connect with:

- **Host:** `postgres` (Docker service name, not `localhost`)
- **Port:** `5432`
- **Database:** `waf_db`
- **Username:** `waf_user`

---

## Build Roadmap

### Week 1 — Core WAF Engine

| Days  | Task                                               | Status     |
|-------|----------------------------------------------------|------------|
| 1–2   | Project setup, Docker, PostgreSQL, Redis, FastAPI  | ✅ Done    |
| 3–4   | Reverse proxy — forward requests, capture metadata | ✅ Done    |
| 5     | Rule Engine — DB-backed regex rules, inspection    | ✅ Done    |
| 6–7   | Threat Scoring Engine + PostgreSQL logging         | ✅ Done    |

### Week 2 — Protection Features

| Days  | Task                                               | Status     |
|-------|----------------------------------------------------|------------|
| 8–9   | Redis rate limiting (sliding window)               | ⬜ Pending |
| 10    | Persistent IP blacklist + auto-block               | ⬜ Pending |
| 11–12 | Admin API (rules, IPs, threshold management)       | ✅ Done    |
| 13–14 | React dashboard with real-time WebSocket logs      | ✅ Done    |

### Week 3 — Advanced (Optional)

- GeoIP blocking
- Bot detection heuristics
- JWT / API key validation
- CI/CD pipeline + cloud deployment
- Prometheus + Grafana monitoring

---

## Useful Commands

```bash
# View WAF logs in real-time
docker compose logs -f waf

# View dashboard build logs
docker compose logs -f dashboard

# Open psql shell
docker compose exec postgres psql -U waf_user -d waf_db

# Open Redis CLI
docker compose exec redis redis-cli

# Rebuild WAF after Python changes
docker compose up --build waf -d

# Rebuild dashboard after React changes
docker compose up --build dashboard -d

# Stop all services (data preserved)
docker compose down

# Stop all services and wipe data volumes
docker compose down -v

# Run Alembic migrations
docker compose exec waf alembic upgrade head
```

---

## Detection Capabilities

13 default rules are seeded automatically on first startup, covering:

| Category          | Rules                                                              |
|-------------------|--------------------------------------------------------------------|
| SQL Injection     | UNION SELECT, tautology (OR 1=1), stacked queries, inline comments |
| XSS               | `<script>` tags, inline event handlers, `javascript:` protocol     |
| Path Traversal    | `../` sequences (raw + URL-encoded), sensitive file names          |
| Command Injection | Shell metacharacters (`;`, `&`) and subshell `$(...)` patterns     |
| SSRF              | Requests targeting localhost / RFC 1918 addresses                  |

Rules are stored in the `waf_rules` table and can be toggled live from the
dashboard without restarting the WAF.

---

## Testing the WAF

All examples hit the NGINX entry point (`http://localhost`), which forwards to
the WAF, which in turn proxies to the backend.

```bash
# 1. Normal request — should be forwarded (action: allow)
curl -s http://localhost/

# 2. SQL Injection — UNION SELECT (score 60 → block)
curl -s "http://localhost/search?q=1'+UNION+SELECT+username,password+FROM+users--"

# 3. XSS — script tag (score 60 → block)
curl -s "http://localhost/page?msg=%3Cscript%3Ealert(1)%3C/script%3E"

# 4. Path Traversal (score 50 → block)
curl -s "http://localhost/files?path=../../etc/passwd"

# 5. Command Injection (score 70 → block)
curl -s "http://localhost/run?cmd=;cat+/etc/passwd"

# 6. Check the attack log after each test
curl -s http://localhost:8000/api/logs | python -m json.tool
```

Blocked requests return HTTP 403:

```json
{"detail": "Request blocked by WAF", "threat_types": ["SQLi"]}
```
