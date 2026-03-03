from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # App
    app_name: str = "iProxy"
    debug: bool = False

    # Database
    database_url: str = "postgresql+asyncpg://iproxy:iproxy123@localhost:5432/iproxy"

    # Redis
    redis_url: str = "redis://localhost:6379/0"

    # JWT
    secret_key: str = "change-me-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60 * 24  # 24 hours

    # CORS
    cors_origins: list[str] = ["http://localhost:3000"]

    # Admin seed
    admin_username: str = "admin"
    admin_password: str = "admin123"

    # Google OAuth
    google_client_id: str = ""
    google_client_secret: str = ""
    google_redirect_uri: str = "http://localhost:8000/api/admin/accounts/oauth/callback"


settings = Settings()
