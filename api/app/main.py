from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.models import User  # noqa: F401 - ensure models are registered
from app.models.api_key import ApiKey  # noqa: F401
from app.models.infra import ProxyPool  # noqa: F401
from app.routers.admin import accounts, auth
from app.services.redis import close_redis, get_redis
from app.services.seed import seed_admin


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await get_redis()
    await seed_admin()
    yield
    # Shutdown
    await close_redis()


app = FastAPI(title=settings.app_name, debug=settings.debug, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix="/api/admin/auth", tags=["auth"])
app.include_router(accounts.router, prefix="/api/admin/accounts", tags=["accounts"])


@app.get("/health")
async def health():
    return {"status": "ok"}
