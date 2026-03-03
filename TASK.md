# Project Tasks: iProxy - API Proxy Đa Tài khoản Google

## Phase 1: Project Setup & Infrastructure

### 1.1 Backend Setup (FastAPI)
- [ ] Setup Python 3.12+ project structure trong `api/`
- [ ] Create `pyproject.toml` với dependencies
- [ ] Setup FastAPI application với CORS cho Next.js trong `admin/`
- [ ] Setup Alembic cho database migrations
- [ ] Setup Redis connection
- [ ] Cấu hình JWT auth cho admin API

### 1.2 Frontend Setup (Next.js)
- [ ] Khởi tạo Next.js 15 project trong `admin/` (TypeScript, App Router)
- [ ] Cài TailwindCSS + shadcn/ui
- [ ] Setup TanStack Query cho API calls
- [ ] Setup Zustand cho client state
- [ ] Tạo API client (`lib/api.ts`) trỏ tới FastAPI
- [ ] Tạo base layout với sidebar navigation

### 1.3 Database Schema
- [ ] Define SQLAlchemy models:
  - `User` - admin user
  - `GoogleAccount` - Google accounts with OAuth tokens
  - `DeviceFingerprint` - device profiles
  - `ApiKey` - API keys for proxy access
  - `ProxyPool` - upstream proxy configs
  - `IpWhitelist` / `IpBlacklist` - IP management
  - `TokenUsage` - usage statistics
  - `RequestLog` - access logs
- [ ] Run initial migrations
- [ ] Seed admin user

---

## Phase 2: Account Management (Google OAuth)

### 2.1 OAuth Flow
- [ ] Implement Google OAuth 2.0 flow (auto & manual)
- [ ] Create OAuth callback handler
- [ ] Store refresh tokens securely
- [ ] Implement token refresh logic

### 2.2 Account CRUD API
- [ ] `GET /api/admin/accounts` — list với filters
- [ ] `POST /api/admin/accounts` — add via OAuth
- [ ] `DELETE /api/admin/accounts/{id}` — delete
- [ ] `POST /api/admin/accounts/batch-delete` — batch delete
- [ ] `POST /api/admin/accounts/import` — import JSON
- [ ] `GET /api/admin/accounts/export` — export JSON

### 2.3 Account Operations API
- [ ] `POST /api/admin/accounts/{id}/refresh-quota`
- [ ] `POST /api/admin/accounts/batch-refresh`
- [ ] `POST /api/admin/accounts/{id}/warmup`
- [ ] 403 Forbidden detection & auto-disable
- [ ] Validation blocking with expiration
- [ ] Protected models per account
- [ ] Account labels & custom naming

### 2.4 Device Fingerprint API
- [ ] `GET/POST /api/admin/accounts/{id}/fingerprint`
- [ ] Capture/generate modes
- [ ] Bind/unbind fingerprint
- [ ] Version history & restore

### 2.5 Accounts Page (Next.js)
- [ ] Grid/list view toggle
- [ ] Search và filter (tier, status)
- [ ] Account detail dialog/sheet
- [ ] Device fingerprint management UI
- [ ] Import/export UI
- [ ] Batch operations UI
- [ ] Pagination

---

## Phase 3: Proxy Engine (Core)

### 3.1 Protocol Support
**OpenAI Compatible:**
- [ ] `POST /v1/chat/completions` (streaming & non-streaming)
- [ ] `POST /v1/completions`
- [ ] `GET /v1/models`
- [ ] `POST /v1/responses`
- [ ] `POST /v1/audio/transcriptions`
- [ ] `POST /v1/images/generations`
- [ ] `POST /v1/images/edits`

**Claude/Anthropic Compatible:**
- [ ] `POST /v1/messages` (with thinking chain)
- [ ] `POST /v1/messages/count_tokens`
- [ ] `GET /v1/models/claude`

**Gemini Native:**
- [ ] `POST /v1beta/models/{model}:generateContent`
- [ ] `POST /v1beta/models/{model}:streamGenerateContent`
- [ ] `GET /v1beta/models`
- [ ] `POST /v1beta/models/{model}:countTokens`

**Utility:**
- [ ] `GET /health`, `GET /healthz`

### 3.2 Smart Routing
- [ ] Implement 5 strategies: Round-Robin, Random, Priority, Least Connections, Weighted
- [ ] Session affinity (CacheFirst/Balance/PerformanceFirst)
- [ ] Tiered routing (Ultra > Pro > Free)
- [ ] Preferred account mode

### 3.3 Circuit Breaker & Resilience
- [ ] Error classification (400/401/403/404/429/500/503)
- [ ] Auto-disable on `invalid_grant`
- [ ] Retry strategies (Fixed/Linear/Exponential backoff)
- [ ] Background task downgrade to Flash model

---

## Phase 4: Proxy Configuration

### 4.1 Proxy Pool API
- [ ] `GET/POST /api/admin/proxy/pool` — CRUD upstream proxies
- [ ] Health check với configurable interval
- [ ] Auto-failover
- [ ] Latency tracking
- [ ] Account-to-proxy binding

### 4.2 Advanced AI Features API
- [ ] `GET/PUT /api/admin/proxy/thinking-budget`
- [ ] `GET/PUT /api/admin/proxy/system-prompt`
- [ ] `GET/PUT /api/admin/proxy/model-mapping`
- [ ] Tool Loop Recovery
- [ ] Context Compression (L1/L2/L3)

### 4.3 MCP Support
- [ ] Web Search MCP endpoint
- [ ] Web Reader MCP endpoint
- [ ] Vision MCP (image/video upload)

### 4.4 Proxy Page (Next.js)
- [ ] Server start/stop control
- [ ] Port và API key config
- [ ] Timeout settings
- [ ] Proxy pool management UI
- [ ] Model mapping UI (regex editor)
- [ ] Thinking budget config UI
- [ ] Global system prompt editor

---

## Phase 5: Security & Access Control

### 5.1 Authentication
- [ ] `POST /api/admin/auth/login` — JWT login
- [ ] `POST /api/admin/auth/logout`
- [ ] Auth middleware cho admin routes
- [ ] Auth modes: off / strict / all_except_health / auto
- [ ] API key authentication (Bearer token)
- [ ] Hot-reload auth config
- [ ] Login page (Next.js)

### 5.2 IP Management API
- [ ] `GET/POST /api/admin/security/whitelist`
- [ ] `GET/POST /api/admin/security/blacklist`
- [ ] CIDR notation support
- [ ] IP access logging
- [ ] IP statistics

### 5.3 Rate Limiting
- [ ] Rate limit per API key
- [ ] Request body size limit (default 100MB)
- [ ] User-Agent override

### 5.4 Security Page (Next.js)
- [ ] IP whitelist management
- [ ] IP blacklist management
- [ ] Access logs viewer
- [ ] IP statistics & ranking

---

## Phase 6: Monitoring & Analytics

### 6.1 Monitor API
- [ ] `GET /api/admin/monitor/stream` — SSE real-time events
- [ ] `GET /api/admin/monitor/requests` — request history
- [ ] `GET /api/admin/monitor/metrics` — performance metrics

### 6.2 Stats API
- [ ] `GET /api/admin/stats/tokens` — token usage (hourly/daily/weekly)
- [ ] `GET /api/admin/stats/models` — per-model breakdown
- [ ] `GET /api/admin/stats/accounts` — per-account breakdown

### 6.3 Dashboard Page (Next.js)
- [ ] Account statistics overview
- [ ] Quota monitoring (Gemini Pro/Image, Claude)
- [ ] Best accounts ranking
- [ ] Low quota alerts
- [ ] Quick actions (Add, Refresh, Export)

### 6.4 Monitor Page (Next.js)
- [ ] Real-time request list (SSE)
- [ ] Network activity tracking
- [ ] Performance metrics

### 6.5 Stats Page (Next.js)
- [ ] Token usage charts (Recharts — hourly/daily/weekly)
- [ ] Per-model breakdown
- [ ] Per-account breakdown
- [ ] Input/output split

---

## Phase 7: API Keys & Settings

### 7.1 API Keys API
- [ ] `GET/POST /api/admin/keys`
- [ ] `PUT/DELETE /api/admin/keys/{id}`
- [ ] IP restrictions (max_ips)
- [ ] Curfew scheduling
- [ ] Expiration settings
- [ ] Usage statistics

### 7.2 Settings API
- [ ] `GET/PUT /api/admin/settings`
- [ ] General, Account, Proxy, Debug sections

### 7.3 API Keys Page (Next.js)
- [ ] Create/edit/delete API keys
- [ ] IP restrictions UI
- [ ] Curfew scheduling UI
- [ ] Expiration settings
- [ ] Usage statistics

### 7.4 Settings Page (Next.js)
- [ ] General settings (theme, language)
- [ ] Account settings
- [ ] Proxy settings
- [ ] Debug settings
- [ ] Cache management

---

## Phase 8: Testing & Deployment

### 8.1 Testing
- [ ] Unit tests cho core logic (pytest)
- [ ] Integration tests cho proxy endpoints
- [ ] OAuth flow testing
- [ ] Frontend component tests (Vitest)

### 8.2 Deployment
- [ ] Dockerfile cho backend
- [ ] Dockerfile cho frontend (Next.js standalone)
- [ ] Docker Compose cho dev (backend + frontend + postgres + redis)
- [ ] Production docker-compose
- [ ] Nginx reverse proxy config
- [ ] Environment variable management

### 8.3 Documentation
- [ ] API documentation (OpenAPI/Swagger — tự động từ FastAPI)
- [ ] User guide
- [ ] Deployment guide

---

## Priority Order (Recommended)

1. **Phase 1** → Project setup (foundation)
2. **Phase 2** → Account management (core data)
3. **Phase 3** → Proxy engine (core functionality)
4. **Phase 5** → Security (needed before production)
5. **Phase 4** → Proxy config (enhancement)
6. **Phase 6** → Monitoring & analytics
7. **Phase 7** → API keys & settings
8. **Phase 8** → Testing & deployment
