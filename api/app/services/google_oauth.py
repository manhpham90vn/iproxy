import httpx
from pydantic import BaseModel

from app.config import settings


class GoogleTokens(BaseModel):
    access_token: str
    refresh_token: str | None
    expires_in: int
    token_type: str


class GoogleUserInfo(BaseModel):
    id: str
    email: str
    name: str | None
    picture: str | None


def get_google_auth_url(state: str | None = None) -> str:
    """Generate the Google OAuth authorization URL."""
    from urllib.parse import urlencode

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile https://www.googleapis.com/auth/gmail.readonly",
        "access_type": "offline",
        "prompt": "consent",
    }
    if state:
        params["state"] = state

    return f"https://accounts.google.com/o/oauth2/v2/auth?{urlencode(params)}"


async def exchange_code_for_tokens(code: str) -> GoogleTokens:
    """Exchange authorization code for access and refresh tokens."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "code": code,
                "grant_type": "authorization_code",
                "redirect_uri": settings.google_redirect_uri,
            },
        )
        response.raise_for_status()
        data = response.json()

    return GoogleTokens(
        access_token=data["access_token"],
        refresh_token=data.get("refresh_token"),
        expires_in=data.get("expires_in", 3600),
        token_type=data.get("token_type", "Bearer"),
    )


async def refresh_google_token(refresh_token: str) -> GoogleTokens:
    """Refresh an expired Google access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "client_id": settings.google_client_id,
                "client_secret": settings.google_client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token",
            },
        )
        response.raise_for_status()
        data = response.json()

    return GoogleTokens(
        access_token=data["access_token"],
        refresh_token=refresh_token,  # Refresh token doesn't change
        expires_in=data.get("expires_in", 3600),
        token_type=data.get("token_type", "Bearer"),
    )


async def get_user_info(access_token: str) -> GoogleUserInfo:
    """Get user profile information from Google."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        response.raise_for_status()
        data = response.json()

    return GoogleUserInfo(
        id=data["id"],
        email=data["email"],
        name=data.get("name"),
        picture=data.get("picture"),
    )


async def revoke_token(access_token: str) -> bool:
    """Revoke a Google access token."""
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://oauth2.googleapis.com/revoke",
            params={"token": access_token},
        )
        return response.status_code == 200
