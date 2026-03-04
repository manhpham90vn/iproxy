from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

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


@dataclass
class HealthCheckResult:
    is_healthy: bool
    is_forbidden: bool
    forbidden_reason: str | None
    error_message: str | None
    quota_data: dict[str, Any] | None


def get_google_auth_url(state: str | None = None) -> str:
    """Generate the Google OAuth authorization URL."""
    from urllib.parse import urlencode

    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": " ".join(
            [
                "openid",
                "email",
                "profile",
                "https://www.googleapis.com/auth/cloud-platform",
                "https://www.googleapis.com/auth/userinfo.email",
                "https://www.googleapis.com/auth/userinfo.profile",
                "https://www.googleapis.com/auth/cclog",
                "https://www.googleapis.com/auth/experimentsandconfigs",
            ]
        ),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
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


CLOUD_CODE_BASE_URL = "https://daily-cloudcode-pa.sandbox.googleapis.com"
QUOTA_API_URL = "https://cloudcode-pa.googleapis.com/v1internal:fetchAvailableModels"
NATIVE_USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
)


async def _fetch_project_and_tier(client: httpx.AsyncClient, access_token: str) -> tuple[str | None, str | None]:
    """Step 1: Call loadCodeAssist to get project_id + subscription_tier."""
    try:
        response = await client.post(
            f"{CLOUD_CODE_BASE_URL}/v1internal:loadCodeAssist",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "User-Agent": NATIVE_USER_AGENT,
            },
            json={"metadata": {"ideType": "ANTIGRAVITY"}},
        )
        if not response.is_success:
            return None, None

        data = response.json()
        project_id: str | None = data.get("cloudaicompanionProject")

        # Multi-level fallback for tier (mirrors Antigravity-Manager logic)
        paid_tier = data.get("paidTier", {}) or {}
        current_tier = data.get("currentTier", {}) or {}
        allowed_tiers: list[dict] = data.get("allowedTiers") or []
        ineligible_tiers: list[dict] = data.get("ineligibleTiers") or []

        subscription_tier: str | None = paid_tier.get("name") or paid_tier.get("id")

        is_ineligible = len(ineligible_tiers) > 0
        if subscription_tier is None:
            if not is_ineligible:
                subscription_tier = current_tier.get("name") or current_tier.get("id")
            else:
                # Restricted: fall back to default allowed tier
                default_tier = next((t for t in allowed_tiers if t.get("is_default")), None)
                if default_tier:
                    base = default_tier.get("name") or default_tier.get("id") or ""
                    subscription_tier = f"{base} (Restricted)" if base else None

        return project_id, subscription_tier
    except Exception:
        return None, None


async def get_account_quota(access_token: str) -> dict[str, Any]:
    """Fetch quota and subscription plan from Google CloudCode APIs.

    Mirrors Antigravity-Manager two-step approach:
    1. loadCodeAssist  → project_id + subscription_tier
    2. fetchAvailableModels → per-model quota percentages
    """
    async with httpx.AsyncClient(timeout=30.0) as client:
        # --- Step 1: Get project_id + plan ---
        project_id, subscription_tier = await _fetch_project_and_tier(client, access_token)

        # --- Step 2: Fetch per-model quota ---
        payload = {"project": project_id} if project_id else {}
        response = await client.post(
            QUOTA_API_URL,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "User-Agent": NATIVE_USER_AGENT,
            },
            json=payload,
        )

        if response.status_code == 403:
            # If loadCodeAssist succeeded (we have a tier), the account itself is NOT forbidden —
            # it just means the Cloud Code quota API isn't accessible for this project.
            # Only mark as truly forbidden when even loadCodeAssist failed.
            if subscription_tier is None:
                return {
                    "is_forbidden": True,
                    "forbidden_reason": response.json().get("error", {}).get("message", "Access forbidden"),
                    "models": [],
                    "subscription_tier": None,
                }
            # We have plan info but no per-model quota → return partial data
            return {
                "is_forbidden": False,
                "forbidden_reason": None,
                "models": [],
                "model_forwarding_rules": {},
                "subscription_tier": subscription_tier,
                "last_updated": datetime.now(timezone.utc).isoformat(),
            }

        response.raise_for_status()
        data = response.json()

    models: list[dict[str, Any]] = []
    model_forwarding_rules: dict[str, str] = {}

    for name, info in (data.get("models") or {}).items():
        # Only keep the model types we care about
        if not any(name.startswith(prefix) for prefix in ("gemini", "claude", "gpt", "image", "imagen")):
            continue

        quota_info = info.get("quotaInfo") or {}
        remaining_fraction = quota_info.get("remainingFraction")
        percentage = int((remaining_fraction or 0.0) * 100)

        models.append(
            {
                "name": name,
                "display_name": info.get("displayName", name),
                "percentage": percentage,
                "reset_time": quota_info.get("resetTime", ""),
                "supports_images": info.get("supportsImages"),
                "supports_thinking": info.get("supportsThinking"),
                "thinking_budget": info.get("thinkingBudget"),
                "recommended": info.get("recommended"),
                "max_tokens": info.get("maxTokens"),
                "max_output_tokens": info.get("maxOutputTokens"),
                "supported_mime_types": info.get("supportedMimeTypes"),
            }
        )

    # Parse deprecated model forwarding rules
    for old_id, dep_info in (data.get("deprecatedModelIds") or {}).items():
        model_forwarding_rules[old_id] = dep_info.get("newModelId", "")

    return {
        "is_forbidden": False,
        "forbidden_reason": None,
        "models": models,
        "model_forwarding_rules": model_forwarding_rules,
        "subscription_tier": subscription_tier,
        "last_updated": datetime.now(timezone.utc).isoformat(),
    }


async def warmup_account(access_token: str) -> dict[str, Any]:
    """Perform a lightweight API call to warm up the account.

    Uses v1internal endpoint (same as Antigravity-Manager) instead of public generativelanguage API.
    This avoids "insufficient authentication scopes" errors.
    """
    # First, get project_id from loadCodeAssist (same as Antigravity-Manager)
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Get project_id via loadCodeAssist
        project_id, _ = await _fetch_project_and_tier(client, access_token)

        if not project_id:
            # Fallback: try direct call to v1internal without project (may work for some accounts)
            warmup_url = f"{CLOUD_CODE_BASE_URL}/v1internal:generateContent"
            body = {
                "model": "gemini-2.0-flash",
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "hi"}]}],
                    "generationConfig": {"temperature": 0},
                },
                "requestType": "agent",
            }
        else:
            # Step 2: Call v1internal:generateContent with project_id
            warmup_url = f"{CLOUD_CODE_BASE_URL}/v1internal:generateContent"
            body = {
                "project": project_id,
                "model": "gemini-2.0-flash",
                "request": {
                    "contents": [{"role": "user", "parts": [{"text": "hi"}]}],
                    "generationConfig": {"temperature": 0},
                },
                "requestType": "agent",
            }

        response = await client.post(
            warmup_url,
            headers={
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json",
                "User-Agent": NATIVE_USER_AGENT,
            },
            json=body,
        )

        if response.status_code == 403:
            error_data = response.json()
            return {
                "success": False,
                "is_forbidden": True,
                "error": error_data.get("error", {}).get("message", "Access forbidden"),
            }
        if response.status_code != 200:
            return {
                "success": False,
                "is_forbidden": False,
                "error": f"HTTP {response.status_code}: {response.text[:200]}",
            }

    return {"success": True, "is_forbidden": False, "error": None}


async def check_account_health(access_token: str) -> HealthCheckResult:
    """Check account health by calling a lightweight API endpoint.

    Uses v1internal endpoint (same as Antigravity-Manager) to avoid scope issues.
    """
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            # Get project_id first via loadCodeAssist
            project_id, _ = await _fetch_project_and_tier(client, access_token)

            if not project_id:
                return HealthCheckResult(
                    is_healthy=False,
                    is_forbidden=True,
                    forbidden_reason="Could not get project_id from account",
                    error_message="Could not get project_id from account",
                    quota_data=None,
                )

            # Use v1internal:loadCodeAssist as health check (same endpoint used for quota)
            response = await client.post(
                f"{CLOUD_CODE_BASE_URL}/v1internal:loadCodeAssist",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                    "User-Agent": NATIVE_USER_AGENT,
                },
                json={"metadata": {"ideType": "ANTIGRAVITY"}},
            )

            if response.status_code == 403:
                error_data = response.json()
                reason = error_data.get("error", {}).get("message", "Access forbidden")
                return HealthCheckResult(
                    is_healthy=False,
                    is_forbidden=True,
                    forbidden_reason=reason,
                    error_message=reason,
                    quota_data=None,
                )
            if response.status_code == 401:
                return HealthCheckResult(
                    is_healthy=False,
                    is_forbidden=False,
                    forbidden_reason=None,
                    error_message="Token expired or invalid",
                    quota_data=None,
                )
            response.raise_for_status()
            quota_data = await get_account_quota(access_token)
            return HealthCheckResult(
                is_healthy=True,
                is_forbidden=False,
                forbidden_reason=None,
                error_message=None,
                quota_data=quota_data,
            )
    except httpx.TimeoutException:
        return HealthCheckResult(
            is_healthy=False,
            is_forbidden=False,
            forbidden_reason=None,
            error_message="Request timed out",
            quota_data=None,
        )
    except Exception as e:
        return HealthCheckResult(
            is_healthy=False,
            is_forbidden=False,
            forbidden_reason=None,
            error_message=str(e),
            quota_data=None,
        )
