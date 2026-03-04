# Development Guide

## Requirements

- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- Git

## Setup

### 1. Clone repo

```bash
git clone <repo-url> && cd iproxy
```

### 2. Backend (FastAPI)

```bash
cd api
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 3. Frontend (Next.js Admin)

```bash
cd admin
npm install
```

### 4. Start PostgreSQL & Redis

```bash
docker compose up -d
```

| Service  | Port | Default |
|----------|------|---------|
| Postgres | 5432 | user: `iproxy`, pass: `iproxy123`, db: `iproxy` |
| Redis    | 6379 | no password |

### 5. Configure environment

```bash
# Backend
cp api/.env.example api/.env

# Frontend
cp admin/.env.example admin/.env.local
```

Important variables in `admin/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 6. Run migrations

```bash
cd api
alembic upgrade head
```

Create new migration when changing models:

```bash
alembic revision --autogenerate -m "description"
alembic upgrade head
```

### 7. Run the app

**Backend:**
```bash
cd api
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd admin
npm run dev
```

Access:
- Admin Panel: http://localhost:3000
- API docs: http://localhost:8000/docs

## Format & Lint

**Backend** uses [Ruff](https://docs.astral.sh/ruff/):

```bash
cd api

# Check linting
ruff check .

# Auto-fix
ruff check . --fix

# Format code
ruff format .
```

Config: line length 120, Python 3.12, rules `E`, `F`, `I`.

**Frontend** uses ESLint + Prettier:

```bash
cd admin

# Lint
npm run lint

# Format
npm run format
```

## Test

```bash
# Backend
cd api && pytest

# Frontend
cd admin && npm test
```

## Project Structure

```
iproxy/
├── api/                     # FastAPI backend
│   ├── app/
│   │   ├── main.py         # FastAPI entry point
│   │   ├── config.py      # Pydantic settings
│   │   ├── database.py    # SQLAlchemy async engine
│   │   ├── models/        # SQLAlchemy models
│   │   ├── routers/       # API route handlers
│   │   │   └── admin/     # Admin API endpoints
│   │   ├── schemas/       # Pydantic schemas
│   │   └── services/      # Business logic
│   ├── alembic/           # Database migrations
│   ├── tests/             # Test suite
│   └── pyproject.toml     # Dependencies
│
├── admin/                  # Next.js frontend
│   ├── src/
│   │   ├── app/          # App Router pages
│   │   ├── components/   # React components
│   │   ├── lib/          # API client, utilities
│   │   └── hooks/        # Custom React hooks
│   └── package.json
│
└── docker-compose.yml      # PostgreSQL + Redis services
```
