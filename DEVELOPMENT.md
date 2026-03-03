# Development Guide

## Yêu cầu

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
cd backend
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

### 3. Frontend (Next.js Admin)

```bash
cd admin
npm install
```

### 4. Khởi động PostgreSQL & Redis

```bash
docker compose up -d
```

| Service  | Port | Mặc định |
|----------|------|-----------|
| Postgres | 5432 | user: `iproxy`, pass: `iproxy123`, db: `iproxy` |
| Redis    | 6379 | không password |

### 5. Cấu hình environment

```bash
# Backend
cp backend/.env.example backend/.env

# Frontend
cp admin/.env.example admin/.env.local
```

Các biến quan trọng trong `admin/.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 6. Chạy migration

```bash
cd backend
alembic upgrade head
```

Tạo migration mới khi thay đổi models:

```bash
alembic revision --autogenerate -m "mô tả thay đổi"
alembic upgrade head
```

### 7. Chạy app

**Backend:**
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd admin
npm run dev
```

Truy cập:
- Admin Panel: http://localhost:3000
- API docs: http://localhost:8000/docs

## Format & Lint

**Backend** dùng [Ruff](https://docs.astral.sh/ruff/):

```bash
cd backend

# Check linting
ruff check .

# Auto-fix
ruff check . --fix

# Format code
ruff format .
```

Cấu hình: line length 120, Python 3.12, rules `E`, `F`, `I`.

**Frontend** dùng ESLint + Prettier:

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
cd backend && pytest

# Frontend
cd admin && npm test
```

## Project Structure

```
iproxy/
├── backend/                  # FastAPI service
│   ├── app/
│   │   ├── main.py           # FastAPI entry point
│   │   ├── config.py         # Pydantic settings
│   │   ├── database.py       # SQLAlchemy async engine
│   │   ├── models/           # ORM models
│   │   ├── routers/          # API routers
│   │   │   ├── admin/        # Admin REST API (/api/admin/*)
│   │   │   └── proxy/        # Proxy endpoints (/v1/*, /v1beta/*, /mcp/*)
│   │   └── services/         # Business logic
│   ├── alembic/              # Database migrations
│   ├── tests/                # Test suite
│   ├── pyproject.toml        # Dependencies & tool config
│   └── .env                  # Environment variables
├── admin/                    # Next.js admin panel
│   ├── src/
│   │   ├── app/              # App Router pages
│   │   ├── components/       # React components
│   │   ├── lib/              # API client, utils
│   │   └── hooks/            # Custom hooks
│   ├── package.json
│   └── .env.local            # Frontend env vars
└── docker-compose.yml        # PostgreSQL + Redis
```
