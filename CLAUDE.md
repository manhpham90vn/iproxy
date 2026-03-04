# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

iProxy is a **multi-account Google API proxy system** that acts as a gateway for accessing Google AI services (Gemini, Claude via Google, etc.) through multiple Google accounts. It consists of:

- **Backend (FastAPI)**: Python 3.12+ proxy engine with multi-protocol support
- **Frontend (Next.js)**: Admin panel for managing accounts, API keys, and monitoring
- **Infrastructure**: PostgreSQL + Redis via Docker Compose

## Common Commands

### Development Setup

```bash
# Start infrastructure (PostgreSQL + Redis)
docker compose up -d

# Backend setup
cd api
python -m venv venv && source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head

# Frontend setup
cd ../admin
npm install
cp .env.example .env.local
```

### Running the Application

```bash
# Backend (port 8000)
cd api && uvicorn app.main:app --reload --port 8000

# Frontend (port 3000)
cd admin && npm run dev
```

### Format & Lint

```bash
# Backend (Ruff)
cd api
ruff check . --fix
ruff format .

# Frontend (ESLint + Prettier)
cd admin
npm run lint
npm run format
```

### Testing

```bash
# Backend
cd api && pytest

# Frontend
cd admin && npm test
```

### Database Migrations

```bash
cd api
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Architecture

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend Framework | FastAPI (Python 3.12+) |
| ORM | SQLAlchemy + Alembic |
| Database | PostgreSQL (prod) / SQLite (dev) |
| Cache | Redis |
| Frontend | Next.js 16 (App Router) |
| UI | TailwindCSS + shadcn/ui + Radix |
| State | TanStack Query + Zustand |

### Project Structure

```
iproxy/
├── api/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── config.py      # Pydantic settings
│   │   ├── database.py    # SQLAlchemy async engine
│   │   ├── models/        # SQLAlchemy models (User, GoogleAccount, ApiKey, ProxyPool)
│   │   ├── routers/       # API route handlers
│   │   │   └── admin/     # Admin API endpoints
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── alembic/           # Database migrations
│   ├── tests/             # Test suite
│   └── pyproject.toml     # Dependencies (Ruff, pytest)
│
├── admin/                  # Next.js frontend
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # React components
│   │   ├── lib/          # API client, utilities
│   │   ├── hooks/        # Custom React hooks
│   │   └── store/        # Zustand state stores
│   └── package.json
│
├── docker-compose.yml      # PostgreSQL + Redis services
└── DEVELOPMENT.md         # Development guide
```

### Key API Endpoints

**Admin API** (prefix: `/api/admin`):
- `POST /api/admin/auth/login` — Admin authentication
- `GET/POST /api/admin/accounts` — Account management
- `GET/POST /api/admin/keys` — API key management

**Proxy API**:
- `/v1/*` — OpenAI compatible endpoints
- `/v1beta/*` — Gemini native endpoints
- `/mcp/*` — MCP protocol endpoints

### Database Models

- **User** — Admin users for panel access
- **GoogleAccount** — Managed Google accounts with OAuth tokens, quotas, fingerprints
- **DeviceFingerprint** — Browser/device fingerprint for account binding
- **ApiKey** — Client API keys with rate limiting, IP restrictions
- **ProxyPool** — Upstream HTTP/SOCKS5 proxy configuration

## Key Configuration

### Backend Environment Variables

```bash
DATABASE_URL=postgresql+asyncpg://iproxy:iproxy123@localhost:5432/iproxy
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=change-me-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

### Frontend Environment Variables

```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Linting Configuration

Backend uses Ruff with line-length 120, Python 3.12, rules `E`, `F`, `I`.
