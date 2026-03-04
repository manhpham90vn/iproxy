# System Design: iProxy - Multi-Account Google API Proxy

## 1. Project Overview

iProxy is a personal-use **Web Application** that acts as a central gateway/proxy for communicating with Google AI services through multiple accounts. The project is based on the features of **Antigravity-Manager** (Tauri v2 desktop app) but ported to a web platform.

Consists of 2 services:
- **FastAPI (Python)**: Proxy Engine + REST API — Streaming, Protocol Translation, Model Routing, Circuit Breaker.
- **Next.js (TypeScript)**: Admin Panel — SPA with React, communicates with FastAPI via REST API.

---

## 2. Core Features

### 2.1 Account & Device Management

- Login and authorization via **Google OAuth 2.0** (auto & manual flow).
- Manage **multiple Google accounts** with quota tracking (FREE/PRO/ULTRA tier).
- **Device Fingerprint** management: capture/generate modes, bind/restore/version history.
- Automatic (scheduled) and manual warmup.
- **Import accounts** in multiple formats: OAuth flow, V1 format, custom database, JSON.
- **Export accounts** to JSON.
- **403 Forbidden detection** — automatically mark and skip blocked accounts.
- **Validation blocking** — manage blocked accounts with expiration time.
- **Protected models** per account — specify allowed models.
- Account labels, custom naming, reordering.
- Batch operations: delete, warmup, refresh quota in bulk.
- Account sync from database.

### 2.2 Proxy Engine (Multi-Protocol)

**OpenAI Compatible:**
- `POST /v1/chat/completions` — Chat completions (streaming & non-streaming).
- `POST /v1/completions` — Text completions.
- `GET /v1/models` — List available models.
- `POST /v1/responses` — Codex CLI compatible.
- `POST /v1/audio/transcriptions` — Whisper API compatible.
- `POST /v1/images/generations` — Image generation.
- `POST /v1/images/edits` — Image editing.

**Claude/Anthropic Compatible:**
- `POST /v1/messages` — Messages API with thinking chain, system prompt.
- `POST /v1/messages/count_tokens` — Token counting.
- `GET /v1/models/claude` — List Claude models.

**Gemini Native:**
- `POST /v1beta/models/{model}:generateContent` — Non-streaming.
- `POST /v1beta/models/{model}:streamGenerateContent` — Streaming.
- `GET /v1beta/models` — List models.
- `GET /v1beta/models/{model}` — Model info.
- `POST /v1beta/models/{model}:countTokens` — Token counting.

**MCP (Model Context Protocol):**
- `POST /mcp/web_search_prime/mcp` — Web Search.
- `POST /mcp/web_reader/mcp` — Web Reader.
- `POST /mcp/zai-mcp-server/mcp` — Vision MCP (built-in).
- Vision tools: `ui_to_artifact`, `extract_text_from_screenshot`, `diagnose_error_screenshot`, `understand_technical_diagram`, `analyze_data_visualization`, `ui_diff_check`, `analyze_image`, `analyze_video`.
- Image support: PNG, JPG, JPEG (max 5MB).
- Video support: MP4, MOV, M4V (max 8MB).

**Utility:**
- `GET /health`, `GET /healthz` — Health check.
- `POST /v1/models/detect` — Model detection.

### 2.3 Smart Routing & Resilience

- **Proxy Pool** with 5 strategies: Round-Robin, Random, Priority, Least Connections, Weighted.
- **Circuit Breaker** — automatically disable account on repeated errors.
  - Retry strategies: Fixed / Linear / Exponential backoff.
  - Auto-disable on `invalid_grant`.
- **Session Affinity** (Sticky Session): CacheFirst / Balance / PerformanceFirst.
- **Error Classification**: 400/401/403/404/429/500/503 → auto-rotate/retry/backoff.
- Account ↔ Proxy binding (persistent).
- **Preferred Account Mode** — fixed account selection for specific requests.
- **Tiered Routing**: Prioritize accounts by tier (Ultra > Pro > Free).
- **Background Task Downgrade**: Automatically redirect background requests (title gen) → Flash model.

### 2.4 Proxy Pool Management

- Manage multiple upstream proxies (HTTP/HTTPS/SOCKS5).
- Automatic health check with configurable interval (default 300s).
- Auto-failover when proxy is down.
- Proxy tags and metadata.
- Latency tracking per proxy.
- Max accounts per proxy limit.
- Account-to-proxy binding.
- Proxy authentication support.

### 2.5 Advanced AI Features

- **Thinking Budget Config**: Auto / Passthrough / Custom / Adaptive modes.
  - Auto-limit for Flash/Thinking models (24576 tokens).
  - Custom fixed value override.
  - Adaptive effort control (low/medium/high).
- **Global System Prompt Injection** into all requests (enable/disable toggle).
- **Image Thinking Mode** toggle (preserve vs remove thinking chains).
- **Model Mapping/Routing**: Custom model name → actual model, regex-level mapping.
- **Tool Loop Recovery**: Auto-close tool loops for thinking models.
- **Context Compression** — 3 levels:
  - L1: Tool trimming.
  - L2: Thinking compression.
  - L3: Fork + summary.
  - Usage scaling for 200k+ context limits.
- **Experimental Features:**
  - Signature cache (double-layer caching).
  - Cross-model compatibility checks.
  - Context usage scaling.
  - Configurable compression thresholds.

### 2.6 API Key Management

- **API Keys** (single key or sub-keys):
  - IP restrictions (max_ips).
  - Curfew scheduling (start/end times).
  - Expiration types: day, week, month, never, custom.
  - Token status tracking (enabled/disabled).
  - Token usage history.
  - Token summary statistics.

### 2.7 Security & Access Control

- **Auth modes**: `off` / `strict` / `all_except_health` / `auto`.
- **Hot-reload** auth configuration — no restart required.
- API key authentication with Bearer token support.
- Rate limiting per API key.
- **IP Management:**
  - Whitelist with CIDR notation support.
  - Blacklist with custom block messages.
  - Whitelist priority mode (whitelist IPs skip blacklist checks).
  - IP access logging and statistics.
  - IP ranking.
- Request body size limit (default 100MB).
- CORS support.
- User-Agent override.

### 2.8 Monitoring & Analytics

**Dashboard:**
- Account statistics overview (total, average quotas).
- Best accounts ranking.
- Quota monitoring per model (Gemini Pro, Gemini Image, Claude).
- Low quota alerts.
- Quick actions: Add account, Refresh quota, Export data.

**Real-time Monitor:**
- Proxy request monitoring.
- Network activity tracking.
- Performance metrics.

**Token Statistics:**
- Token usage analytics: hourly / daily / weekly views.
- Per-model breakdown.
- Per-account breakdown.
- Model & account trend analysis.
- Input/output token split.
- Request count tracking.
- Summary statistics (total tokens, requests, unique accounts).

**Debug Logging:**
- Full request/response logging to files.
- Configurable output directory.
- Debug console with log bridge.
- Log filtering and clearing.

---

## 3. Admin Panel (Next.js)

SPA built with Next.js (App Router), communicates with FastAPI via REST API (`/api/admin/*`).

| # | Page | Route | Description |
|---|------|-------|-------------|
| 1 | Dashboard | `/` | Account overview, quotas, quick actions |
| 2 | Accounts | `/accounts` | CRUD accounts, import/export, batch ops, fingerprint |
| 3 | API Proxy | `/proxy` | Proxy config, pool, model mapping, thinking budget |
| 4 | Monitor | `/monitor` | Real-time proxy monitoring, network activity (SSE) |
| 5 | Token Stats | `/stats` | Token usage analytics, trends, breakdowns |
| 6 | API Keys | `/keys` | Manage API keys, IP limits, curfew |
| 7 | Security | `/security` | IP whitelist/blacklist, access logs, IP stats |
| 8 | Settings | `/settings` | General, Account, Proxy, Advanced, Debug tabs |

---

## 4. Technical Architecture

### Tech Stack

**Backend (FastAPI):**
- **Framework**: FastAPI (Python 3.12+)
- **ORM**: SQLAlchemy + Alembic (migrations)
- **Database**: SQLite (dev) / PostgreSQL (prod)
- **Cache**: Redis
- **Task Queue**: ARQ (async Redis queue)
- **HTTP Client**: httpx (async, streaming)

**Frontend (Next.js Admin):**
- **Framework**: Next.js 15+ (App Router, TypeScript)
- **UI**: TailwindCSS + shadcn/ui
- **State**: TanStack Query (server state) + Zustand (client state)
- **Charts**: Recharts
- **Real-time**: EventSource (SSE from FastAPI)

### Routes

**Admin REST API (FastAPI — prefix `/api/admin`):**
- `GET/POST /api/admin/accounts` — Account management
- `GET/POST /api/admin/proxy` — Proxy config
- `GET /api/admin/monitor/stream` — SSE real-time events
- `GET /api/admin/stats` — Token statistics
- `GET/POST /api/admin/keys` — API keys
- `GET/POST /api/admin/security` — IP management
- `GET/PUT /api/admin/settings` — Settings
- `POST /api/admin/auth/login` — Admin login (JWT)

**Proxy API (FastAPI):**
- `/v1/*` — OpenAI compatible endpoints.
- `/v1/messages/*` — Claude compatible endpoints.
- `/v1beta/*` — Gemini native endpoints.
- `/mcp/*` — MCP endpoints.
