from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models import AccountStatus, AccountTier, User
from app.routers.admin.auth import get_current_user
from app.schemas import (
    AccountCreate,
    AccountList,
    AccountResponse,
    AccountUpdate,
    BatchDeleteResponse,
    BatchIdsRequest,
    BatchRefreshResponse,
    CurrentAccountResponse,
    ExportResponse,
    FingerprintCreate,
    FingerprintResponse,
    FingerprintVersionResponse,
    ImportRequest,
    ImportResponse,
    ProtectedModelsRequest,
    ReorderRequest,
    SwitchAccountResponse,
    ToggleProxyRequest,
    ValidationBlockRequest,
    WarmupResponse,
)
from app.services import account as account_service

router = APIRouter()


# OAuth endpoints


class OAuthUrlResponse(BaseModel):
    url: str


class OAuthCallbackResponse(BaseModel):
    message: str
    account_id: int | None = None


@router.get("/oauth/url", response_model=OAuthUrlResponse)
async def get_oauth_url(current_user: User = Depends(get_current_user)):
    from app.config import settings
    from app.services import google_oauth as oauth_service

    if not settings.google_client_id or not settings.google_client_secret:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Google OAuth not configured. Please set GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET in environment.",
        )

    url = oauth_service.get_google_auth_url()
    return OAuthUrlResponse(url=url)


@router.get("/oauth/callback", response_class=HTMLResponse)
async def oauth_callback(code: str | None = None, error: str | None = None, db: AsyncSession = Depends(get_db)):
    from app.services import google_oauth as oauth_service

    # Handle error from Google
    if error:
        return HTMLResponse(
            content=f"""
            <html>
            <head><title>OAuth Error</title></head>
            <body>
                <script>
                    window.opener.postMessage({{ type: 'oauth_error', error: '{error}' }}, '*');
                    window.close();
                </script>
                <p>Error: {error}</p>
            </body>
            </html>
            """,
            status_code=400,
        )

    if not code:
        return HTMLResponse(
            content="""
            <html>
            <head><title>OAuth Error</title></head>
            <body>
                <script>
                    window.opener.postMessage({ type: 'oauth_error', error: 'No authorization code received' }, '*');
                    window.close();
                </script>
                <p>No authorization code received</p>
            </body>
            </html>
            """,
            status_code=400,
        )

    try:
        tokens = await oauth_service.exchange_code_for_tokens(code)
        user_info = await oauth_service.get_user_info(tokens.access_token)
        existing = await account_service.get_account_by_email(db, user_info.email)
        if existing:
            account = await account_service.refresh_account_token(
                db,
                existing,
                access_token=tokens.access_token,
                refresh_token=tokens.refresh_token,
                expires_in=tokens.expires_in,
            )
            account_id = account.id
            message = "Account updated"
        else:
            account = await account_service.create_account(
                db,
                email=user_info.email,
                name=user_info.name,
                refresh_token=tokens.refresh_token,
                access_token=tokens.access_token,
            )
            account_id = account.id
            message = "Account created"

        # Return HTML that communicates with parent window
        post_message = (
            f"window.opener.postMessage({{ type: 'oauth_success', "
            f"account_id: {account_id}, message: '{message}' }}, '*');"
        )
        return HTMLResponse(
            content=f"""
            <html>
            <head><title>OAuth Success</title></head>
            <body>
                <script>
                    {post_message}
                    setTimeout(() => window.close(), 1000);
                </script>
                <p>{message} - You can close this window</p>
            </body>
            </html>
            """,
        )
    except Exception as e:
        error_msg = str(e).replace("'", "\\'")
        return HTMLResponse(
            content=f"""
            <html>
            <head><title>OAuth Error</title></head>
            <body>
                <script>
                    window.opener.postMessage({{ type: 'oauth_error', error: '{error_msg}' }}, '*');
                    window.close();
                </script>
                <p>OAuth failed: {error_msg}</p>
            </body>
            </html>
            """,
            status_code=400,
        )


# Current account


@router.get("/current", response_model=CurrentAccountResponse)
async def get_current_account(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_current_account(db)
    if account:
        return CurrentAccountResponse(account=AccountResponse.model_validate(account))
    return CurrentAccountResponse(account=None)


# List accounts


@router.get("", response_model=AccountList)
async def list_accounts(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    tier: AccountTier | None = None,
    status: AccountStatus | None = None,
    search: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    accounts, total = await account_service.get_accounts(
        db, page=page, page_size=page_size, tier=tier, status=status, search=search
    )
    return AccountList(
        items=[AccountResponse.model_validate(acc) for acc in accounts],
        total=total,
        page=page,
        page_size=page_size,
    )


# Create account manually


@router.post("", response_model=AccountResponse, status_code=status.HTTP_201_CREATED)
async def create_account(
    account_data: AccountCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check if email already exists
    existing = await account_service.get_account_by_email(db, account_data.email)
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Account with this email already exists")

    account = await account_service.create_account(
        db,
        email=account_data.email,
        name=account_data.name,
        label=account_data.label,
        custom_label=account_data.custom_label,
        tier=account_data.tier,
        refresh_token=account_data.refresh_token,
        access_token=account_data.access_token,
        token_expiry=account_data.token_expiry,
        proxy_id=account_data.proxy_id,
    )
    return AccountResponse.model_validate(account)


# Switch current account (must be before /{account_id})


@router.post("/switch-account", response_model=SwitchAccountResponse)
async def switch_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    try:
        account = await account_service.switch_account(db, account_id)
        return SwitchAccountResponse(account_id=account.id, message="Account switched successfully")
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Reorder accounts (must be before /{account_id})


@router.post("/reorder", status_code=status.HTTP_204_NO_CONTENT)
async def reorder_accounts(
    request: ReorderRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    await account_service.reorder_accounts(db, request.account_ids)


# Batch delete (must be before /{account_id})


@router.post("/batch-delete", response_model=BatchDeleteResponse)
async def batch_delete_accounts(
    request: BatchIdsRequest,
    hard: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    deleted = 0
    for account_id in request.account_ids:
        account = await account_service.get_account(db, account_id)
        if account:
            await account_service.delete_account(db, account, hard=hard)
            deleted += 1

    return BatchDeleteResponse(deleted=deleted, total=len(request.account_ids))


# Batch refresh (must be before /{account_id})


@router.post("/batch-refresh", response_model=BatchRefreshResponse)
async def batch_refresh_accounts(
    request: BatchIdsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    refreshed = 0
    failed = 0
    for account_id in request.account_ids:
        account = await account_service.get_account(db, account_id)
        if account:
            _, result = await account_service.refresh_account_quota(db, account)
            if result.get("success"):
                refreshed += 1
            else:
                failed += 1
        else:
            failed += 1

    return BatchRefreshResponse(refreshed=refreshed, failed=failed, total=len(request.account_ids))


# Refresh all accounts (must be before /{account_id})


@router.post("/refresh-all", response_model=BatchRefreshResponse)
async def refresh_all_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    accounts = await account_service.get_all_accounts(db)
    refreshed = 0
    failed = 0
    for account in accounts:
        _, result = await account_service.refresh_account_quota(db, account)
        if result.get("success"):
            refreshed += 1
        else:
            failed += 1

    return BatchRefreshResponse(refreshed=refreshed, failed=failed, total=len(accounts))


# Batch warmup (must be before /{account_id})


@router.post("/batch-warmup", response_model=BatchRefreshResponse)
async def batch_warmup_accounts(
    request: BatchIdsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    refreshed = 0
    failed = 0
    for account_id in request.account_ids:
        account = await account_service.get_account(db, account_id)
        if account:
            result = await account_service.do_warmup(db, account)
            if result.get("success"):
                refreshed += 1
            else:
                failed += 1
        else:
            failed += 1

    return BatchRefreshResponse(refreshed=refreshed, failed=failed, total=len(request.account_ids))


# Warmup all accounts (must be before /{account_id})


@router.post("/warmup-all", response_model=BatchRefreshResponse)
async def warmup_all_accounts(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    accounts = await account_service.get_all_accounts(db)
    refreshed = 0
    failed = 0
    for account in accounts:
        result = await account_service.do_warmup(db, account)
        if result.get("success"):
            refreshed += 1
        else:
            failed += 1

    return BatchRefreshResponse(refreshed=refreshed, failed=failed, total=len(accounts))


# Import accounts (must be before /{account_id})


@router.post("/import", response_model=ImportResponse)
async def import_accounts(
    request: ImportRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    imported = await account_service.import_accounts(db, request.accounts)
    return ImportResponse(imported=imported, total=len(request.accounts))


# Export accounts (must be before /{account_id})


@router.get("/export", response_model=ExportResponse)
async def export_accounts(
    account_ids: str | None = Query(None, description="Comma-separated account IDs"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ids = [int(x.strip()) for x in account_ids.split(",")] if account_ids else None
    accounts = await account_service.export_accounts(db, ids)
    return ExportResponse(accounts=accounts)


# Get account by ID


@router.get("/{account_id}", response_model=AccountResponse)
async def get_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    return AccountResponse.model_validate(account)


# Update account


@router.put("/{account_id}", response_model=AccountResponse)
async def update_account(
    account_id: int,
    account_data: AccountUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    account = await account_service.update_account(
        db,
        account,
        name=account_data.name,
        label=account_data.label,
        custom_label=account_data.custom_label,
        tier=account_data.tier,
        status=account_data.status,
        proxy_id=account_data.proxy_id,
    )
    return AccountResponse.model_validate(account)


# Delete account


@router.delete("/{account_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(
    account_id: int,
    hard: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")
    await account_service.delete_account(db, account, hard=hard)


# Toggle proxy


@router.post("/{account_id}/toggle-proxy", response_model=AccountResponse)
async def toggle_proxy(
    account_id: int,
    request: ToggleProxyRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    account = await account_service.toggle_proxy(db, account, enabled=request.enabled, reason=request.reason)
    return AccountResponse.model_validate(account)


# Warmup account


@router.post("/{account_id}/warmup", response_model=WarmupResponse)
async def warmup_account(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    result = await account_service.do_warmup(db, account)

    status_str = "success" if result.get("success") else ("forbidden" if result.get("is_forbidden") else "error")
    return WarmupResponse(
        account_id=account_id,
        status=status_str,
        message=result.get("error", "Warmup completed successfully")
        if not result.get("success")
        else "Warmup completed successfully",
        is_forbidden=result.get("is_forbidden", False),
    )


# Refresh quota


@router.post("/{account_id}/refresh-quota")
async def refresh_quota(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    account, result = await account_service.refresh_account_quota(db, account)
    return {
        "account": AccountResponse.model_validate(account).model_dump(),
        "log": result,
    }


# Validation block


@router.post("/{account_id}/validation-block", response_model=AccountResponse)
async def set_validation_block(
    account_id: int,
    request: ValidationBlockRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    account = await account_service.set_validation_blocked(
        db,
        account,
        blocked=request.blocked,
        reason=request.reason,
        url=request.url,
        until=request.until,
    )
    return AccountResponse.model_validate(account)


# Protected models


@router.put("/{account_id}/protected-models", response_model=AccountResponse)
async def set_protected_models(
    account_id: int,
    request: ProtectedModelsRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    account = await account_service.set_protected_models(db, account, request.models)
    return AccountResponse.model_validate(account)


# Get fingerprint


@router.get("/{account_id}/fingerprint", response_model=FingerprintResponse)
async def get_fingerprint(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    if not account.fingerprint:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Fingerprint not found")

    return FingerprintResponse.model_validate(account.fingerprint)


# Create or update fingerprint


@router.post("/{account_id}/fingerprint", response_model=FingerprintResponse)
async def create_or_update_fingerprint(
    account_id: int,
    fingerprint_data: FingerprintCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    fingerprint = await account_service.get_or_create_fingerprint(
        db,
        account_id=account_id,
        user_agent=fingerprint_data.user_agent,
        accept_language=fingerprint_data.accept_language,
        platform=fingerprint_data.platform,
        data=fingerprint_data.data,
        machine_id=fingerprint_data.machine_id,
        mac_machine_id=fingerprint_data.mac_machine_id,
        dev_device_id=fingerprint_data.dev_device_id,
        sqm_id=fingerprint_data.sqm_id,
    )
    return FingerprintResponse.model_validate(fingerprint)


# Delete fingerprint


@router.delete("/{account_id}/fingerprint", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fingerprint(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    await account_service.delete_fingerprint(db, account_id)


# Get fingerprint versions


@router.get("/{account_id}/fingerprint/versions", response_model=list[FingerprintVersionResponse])
async def get_fingerprint_versions(
    account_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    versions = await account_service.get_fingerprint_versions(db, account_id)
    return [FingerprintVersionResponse.model_validate(v) for v in versions]


# Save fingerprint version


@router.post("/{account_id}/fingerprint/versions", response_model=FingerprintVersionResponse)
async def save_fingerprint_version(
    account_id: int,
    label: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    try:
        version = await account_service.save_fingerprint_version(db, account_id, label)
        return FingerprintVersionResponse.model_validate(version)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


# Restore fingerprint version


@router.post("/{account_id}/fingerprint/versions/{version_id}/restore", response_model=FingerprintResponse)
async def restore_fingerprint_version(
    account_id: int,
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    try:
        fingerprint = await account_service.restore_fingerprint_version(db, account_id, version_id)
        return FingerprintResponse.model_validate(fingerprint)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


# Delete fingerprint version


@router.delete("/{account_id}/fingerprint/versions/{version_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_fingerprint_version(
    account_id: int,
    version_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    account = await account_service.get_account(db, account_id)
    if not account:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Account not found")

    await account_service.delete_fingerprint_version(db, account_id, version_id)
