# Development Guide

## Requirements

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- Git

## Quick Start (Docker)

Run all services in Docker:

```bash
docker compose up -d
```

Services:
- **API**: http://localhost:8000
- **Admin**: http://localhost:3000
- **Postgres**: localhost:5432
- **Redis**: localhost:6379

## Local Development

### Option 1: Full Local

Start infrastructure only:

```bash
docker compose up -d postgres redis
```

Then run services locally:

**Backend:**
```bash
cd api
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd admin
npm install
cp .env.example .env.local
npm run dev
```

### Option 2: Mixed (Backend local, Frontend Docker)

```bash
docker compose up -d postgres redis admin
# Run API locally
cd api && source venv/bin/activate && uvicorn app.main:app --reload --port 8000
```

## Format & Lint

### Backend (Ruff)

```bash
cd api
ruff check . --fix
ruff format .
```

Config: line length 120, Python 3.12, rules `E`, `F`, `I`.

### Frontend (ESLint + Prettier)

```bash
cd admin
npm run lint
npm run format
```

## Testing

```bash
# Backend
cd api && pytest

# Frontend
cd admin && npm test
```

## Database Migrations

```bash
cd api
alembic revision --autogenerate -m "description"
alembic upgrade head
```

## Project Structure

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
└── docker-compose.yml      # All services (Postgres + Redis + API + Admin)
```

## Configuration

### Environment Variables

**Backend** (`api/.env`):
```bash
DATABASE_URL=postgresql+asyncpg://admin:admin@postgres:5432/iproxy
REDIS_URL=redis://redis:6379/0
SECRET_KEY=change-me-in-production
ADMIN_USERNAME=admin
ADMIN_PASSWORD=admin123
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

**Frontend** (`admin/.env.local`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Architecture

### Tech Stack

| Layer | Technology |
|-------|------------|
| Backend Framework | FastAPI (Python 3.12+) |
| ORM | SQLAlchemy + Alembic |
| Database | PostgreSQL |
| Cache | Redis |
| Frontend | Next.js 16 (App Router) |
| UI | TailwindCSS + shadcn/ui + Radix |
| State | TanStack Query + Zustand |

### Key API Endpoints

**Admin API** (prefix: `/api/admin`):
- `POST /api/admin/auth/login` — Admin authentication
- `GET/POST /api/admin/accounts` — Account management
- `GET/POST /api/admin/keys` — API key management

**Proxy API**:
- `/v1/*` — OpenAI compatible endpoints
- `/v1beta/*` — Gemini native endpoints
- `/mcp/*` — MCP protocol endpoints
