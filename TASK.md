# Project Tasks: iProxy - Multi-Account Google API Proxy

## Phase 1: Project Setup & Infrastructure ✅ DONE

### 1.1 Backend Setup (FastAPI)
- [x] Setup Python 3.12+ project structure in `api/`
- [x] Create `pyproject.toml` with dependencies
- [x] Setup FastAPI application with CORS for Next.js in `admin/`
- [x] Setup Alembic for database migrations
- [x] Setup Redis connection
- [x] Configure JWT auth for admin API

### 1.2 Frontend Setup (Next.js)
- [x] Initialize Next.js project in `admin/` (TypeScript, App Router)
- [x] Install TailwindCSS + shadcn/ui
- [x] Setup TanStack Query for API calls
- [x] Setup Zustand for client state
- [x] Create API client (`lib/api.ts`) pointing to FastAPI
- [x] Create base layout with sidebar navigation

### 1.3 Database Schema
- [x] Define SQLAlchemy models:
  - [x] `User` - admin user
  - [x] `GoogleAccount` - Google accounts with OAuth tokens
  - [x] `DeviceFingerprint` - device profiles
  - [x] `ApiKey` - API keys for proxy access
  - [x] `ProxyPool` - upstream proxy configs
  - [x] `IpWhitelist` / `IpBlacklist` - IP management
  - [x] `TokenUsage` - usage statistics
  - [x] `RequestLog` - access logs
- [x] Run initial migrations
- [x] Seed admin user

---

## Phase 2: Account Management (Google OAuth) ✅ DONE

### 2.1 OAuth Flow
- [x] Implement Google OAuth 2.0 flow (auto & manual)
- [x] Create OAuth callback handler
- [x] Store refresh tokens securely
- [x] Implement token refresh logic

### 2.2 Account CRUD API
- [x] `GET /api/admin/accounts` — list with filters
- [x] `POST /api/admin/accounts` — add via OAuth
- [x] `DELETE /api/admin/accounts/{id}` — delete
- [x] `POST /api/admin/accounts/batch-delete` — batch delete
- [x] `POST /api/admin/accounts/import` — import JSON
- [x] `GET /api/admin/accounts/export` — export JSON

### 2.3 Account Operations API
- [x] `POST /api/admin/accounts/{id}/refresh-quota`
- [x] `POST /api/admin/accounts/batch-refresh`
- [x] `POST /api/admin/accounts/{id}/warmup`
- [x] 403 Forbidden detection & auto-disable
- [x] Validation blocking with expiration
- [x] Protected models per account
- [x] Account labels & custom naming
- [x] Account switch (current account)

### 2.4 Device Fingerprint API
- [x] `GET/POST /api/admin/accounts/{id}/fingerprint`
- [x] Capture/generate modes
- [x] Bind/unbind fingerprint
- [x] Version history & restore

### 2.5 Accounts Page (Next.js)
- [x] Table view
- [x] Search and filter (tier, status)
- [x] Account detail
- [x] Device fingerprint management UI
- [x] Import/export UI
- [x] Batch operations UI
- [x] Pagination
- [x] Account reordering

---

## Phase 3: Proxy Engine (Core) ❌ NOT STARTED

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

## Phase 4: Proxy Configuration ❌ NOT STARTED

### 4.1 Proxy Pool API
- [ ] `GET/POST /api/admin/proxy/pool` — CRUD upstream proxies
- [ ] Health check with configurable interval
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
- [ ] Port and API key config
- [ ] Timeout settings
- [ ] Proxy pool management UI
- [ ] Model mapping UI (regex editor)
- [ ] Thinking budget config UI
- [ ] Global system prompt editor

---

## Phase 5: Security & Access Control ❌ NOT STARTED

### 5.1 Authentication
- [ ] `POST /api/admin/auth/login` — JWT login
- [ ] `POST /api/admin/auth/logout`
- [ ] Auth middleware for admin routes
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

## Phase 6: Monitoring & Analytics ⚠️ PARTIAL

### 6.1 Monitor API
- [ ] `GET /api/admin/monitor/stream` — SSE real-time events
- [ ] `GET /api/admin/monitor/requests` — request history
- [ ] `GET /api/admin/monitor/metrics` — performance metrics

### 6.2 Stats API
- [ ] `GET /api/admin/stats/tokens` — token usage (hourly/daily/weekly)
- [ ] `GET /api/admin/stats/models` — per-model breakdown
- [ ] `GET /api/admin/stats/accounts` — per-account breakdown

### 6.3 Dashboard Page (Next.js)
- [x] Account statistics overview
- [x] Quota monitoring (Gemini Pro/Image, Claude)
- [x] Best accounts ranking
- [x] Low quota alerts
- [x] Quick actions (Add, Refresh, Export)

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

## Phase 7: API Keys & Settings ❌ NOT STARTED

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

## Phase 8: Testing & Deployment ⚠️ PARTIAL

### 8.1 Testing
- [ ] Unit tests for core logic (pytest)
- [ ] Integration tests for proxy endpoints
- [ ] OAuth flow testing
- [ ] Frontend component tests (Vitest)

### 8.2 Deployment
- [ ] Dockerfile for backend
- [ ] Dockerfile for frontend (Next.js standalone)
- [x] Docker Compose for dev (backend + frontend + postgres + redis)
- [ ] Production docker-compose
- [ ] Nginx reverse proxy config
- [ ] Environment variable management

### 8.3 Documentation
- [x] API documentation (OpenAPI/Swagger — auto-generated from FastAPI)
- [x] README.md
- [x] DEVELOPMENT.md

---

## Priority Order (Recommended)

1. **Phase 1** → Project setup (foundation) ✅ DONE
2. **Phase 2** → Account management (core data) ✅ DONE
3. **Phase 3** → Proxy engine (core functionality)
4. **Phase 5** → Security (needed before production)
5. **Phase 4** → Proxy config (enhancement)
6. **Phase 6** → Monitoring & analytics
7. **Phase 7** → API keys & settings
8. **Phase 8** → Testing & deployment
