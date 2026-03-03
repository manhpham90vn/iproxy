import json
from datetime import datetime, timedelta, timezone
from typing import Any

from sqlalchemy import and_, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import AccountStatus, AccountTier, DeviceFingerprint, DeviceFingerprintVersion, GoogleAccount


async def create_account(
    db: AsyncSession,
    email: str,
    name: str | None = None,
    label: str | None = None,
    custom_label: str | None = None,
    tier: AccountTier = AccountTier.free,
    refresh_token: str | None = None,
    access_token: str | None = None,
    token_expiry: datetime | None = None,
    proxy_id: int | None = None,
) -> GoogleAccount:
    """Create a new Google account."""
    # Get max sort_order
    result = await db.execute(select(func.max(GoogleAccount.sort_order)).where(GoogleAccount.is_current.is_(False)))
    max_order = result.scalar() or 0

    account = GoogleAccount(
        email=email,
        name=name,
        label=label,
        custom_label=custom_label,
        tier=tier,
        status=AccountStatus.active,
        sort_order=max_order + 1,
        refresh_token=refresh_token,
        access_token=access_token,
        token_expiry=token_expiry,
        proxy_id=proxy_id,
    )
    db.add(account)
    await db.commit()
    await db.refresh(account)
    return account


async def get_accounts(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 20,
    tier: AccountTier | None = None,
    status: AccountStatus | None = None,
    search: str | None = None,
) -> tuple[list[GoogleAccount], int]:
    """Get paginated list of accounts with optional filters."""
    query = select(GoogleAccount).options(selectinload(GoogleAccount.fingerprint))

    # Apply filters
    conditions = []
    if tier:
        conditions.append(GoogleAccount.tier == tier)
    if status:
        conditions.append(GoogleAccount.status == status)
    if search:
        conditions.append(
            (GoogleAccount.email.ilike(f"%{search}%"))
            | (GoogleAccount.name.ilike(f"%{search}%"))
            | (GoogleAccount.custom_label.ilike(f"%{search}%"))
        )

    if conditions:
        query = query.where(and_(*conditions))

    # Get total count
    count_query = select(func.count()).select_from(query.subquery())
    total_result = await db.execute(count_query)
    total = total_result.scalar() or 0

    # Apply pagination and sorting
    offset = (page - 1) * page_size
    query = query.offset(offset).limit(page_size).order_by(GoogleAccount.sort_order.asc())

    result = await db.execute(query)
    accounts = list(result.scalars().all())

    return accounts, total


async def get_account(db: AsyncSession, account_id: int) -> GoogleAccount | None:
    """Get a single account by ID."""
    query = (
        select(GoogleAccount)
        .options(
            selectinload(GoogleAccount.fingerprint),
            selectinload(GoogleAccount.fingerprint_versions),
        )
        .where(GoogleAccount.id == account_id)
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_account_by_email(db: AsyncSession, email: str) -> GoogleAccount | None:
    """Get a single account by email."""
    query = select(GoogleAccount).options(selectinload(GoogleAccount.fingerprint)).where(GoogleAccount.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_current_account(db: AsyncSession) -> GoogleAccount | None:
    """Get the current active account."""
    query = (
        select(GoogleAccount).options(selectinload(GoogleAccount.fingerprint)).where(GoogleAccount.is_current.is_(True))
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_all_accounts(db: AsyncSession) -> list[GoogleAccount]:
    """Get all accounts without pagination."""
    query = (
        select(GoogleAccount).options(selectinload(GoogleAccount.fingerprint)).order_by(GoogleAccount.sort_order.asc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def update_account(
    db: AsyncSession,
    account: GoogleAccount,
    name: str | None = None,
    label: str | None = None,
    custom_label: str | None = None,
    tier: AccountTier | None = None,
    status: AccountStatus | None = None,
    proxy_id: int | None = None,
) -> GoogleAccount:
    """Update an account's fields."""
    if name is not None:
        account.name = name
    if label is not None:
        account.label = label
    if custom_label is not None:
        account.custom_label = custom_label
    if tier is not None:
        account.tier = tier
    if status is not None:
        account.status = status
    if proxy_id is not None:
        account.proxy_id = proxy_id

    await db.commit()
    await db.refresh(account)
    return account


async def delete_account(db: AsyncSession, account: GoogleAccount, hard: bool = False) -> None:
    """Delete an account (soft delete by default)."""
    if hard:
        # Delete fingerprint versions first
        for version in account.fingerprint_versions:
            await db.delete(version)
        if account.fingerprint:
            await db.delete(account.fingerprint)
        await db.delete(account)
    else:
        account.status = AccountStatus.disabled
        account.disabled_at = datetime.now(timezone.utc)
    await db.commit()


async def switch_account(db: AsyncSession, account_id: int) -> GoogleAccount:
    """Switch to a different account."""
    # First, unset current flag from all accounts
    await db.execute(update(GoogleAccount).values(is_current=False))

    # Then set current to the selected account
    account = await get_account(db, account_id)
    if not account:
        raise ValueError("Account not found")

    account.is_current = True
    account.last_used = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(account)
    return account


async def toggle_proxy(
    db: AsyncSession,
    account: GoogleAccount,
    enabled: bool,
    reason: str | None = None,
) -> GoogleAccount:
    """Toggle proxy status for an account."""
    account.proxy_disabled = not enabled
    if enabled:
        account.proxy_disabled_reason = None
        account.proxy_disabled_at = None
    else:
        account.proxy_disabled_reason = reason
        account.proxy_disabled_at = datetime.now(timezone.utc)

    await db.commit()
    await db.refresh(account)
    return account


async def reorder_accounts(db: AsyncSession, account_ids: list[int]) -> None:
    """Reorder accounts based on provided list."""
    for idx, account_id in enumerate(account_ids):
        await db.execute(update(GoogleAccount).where(GoogleAccount.id == account_id).values(sort_order=idx))
    await db.commit()


async def refresh_account_token(
    db: AsyncSession,
    account: GoogleAccount,
    access_token: str,
    refresh_token: str | None = None,
    expires_in: int = 3600,
) -> GoogleAccount:
    """Update account with new tokens."""
    account.access_token = access_token
    if refresh_token:
        account.refresh_token = refresh_token
    account.token_expiry = datetime.now(timezone.utc) + timedelta(seconds=expires_in)
    account.status = AccountStatus.active
    await db.commit()
    await db.refresh(account)
    return account


async def update_quota(
    db: AsyncSession,
    account: GoogleAccount,
    quota_data: dict[str, Any],
) -> GoogleAccount:
    """Update account quota data."""
    account.quota_data = json.dumps(quota_data)
    account.quota_updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(account)
    return account


async def set_validation_blocked(
    db: AsyncSession,
    account: GoogleAccount,
    blocked: bool,
    reason: str | None = None,
    url: str | None = None,
    until: datetime | None = None,
) -> GoogleAccount:
    """Set validation blocked status for an account."""
    account.validation_blocked = blocked
    if blocked:
        account.validation_blocked_reason = reason
        account.validation_blocked_until = until
        account.validation_url = url
    else:
        account.validation_blocked_reason = None
        account.validation_blocked_until = None
        account.validation_url = None

    await db.commit()
    await db.refresh(account)
    return account


async def import_accounts(db: AsyncSession, accounts_data: list[dict[str, Any]]) -> int:
    """Bulk import accounts from a list of data dicts."""
    imported = 0
    for data in accounts_data:
        email = data.get("email")
        if not email:
            continue

        # Check if account already exists
        existing = await get_account_by_email(db, email)
        if existing:
            continue

        await create_account(
            db=db,
            email=email,
            name=data.get("name"),
            label=data.get("label"),
            custom_label=data.get("custom_label"),
            tier=AccountTier(data.get("tier", "free")),
            refresh_token=data.get("refresh_token"),
            access_token=data.get("access_token"),
            proxy_id=data.get("proxy_id"),
        )
        imported += 1

    return imported


async def export_accounts(db: AsyncSession, account_ids: list[int] | None = None) -> list[dict[str, Any]]:
    """Export accounts as a list of data dicts."""
    if account_ids:
        query = select(GoogleAccount).where(GoogleAccount.id.in_(account_ids))
    else:
        query = select(GoogleAccount)

    result = await db.execute(query)
    accounts = result.scalars().all()

    return [
        {
            "id": acc.id,
            "email": acc.email,
            "name": acc.name,
            "label": acc.label,
            "custom_label": acc.custom_label,
            "tier": acc.tier.value,
            "status": acc.status.value,
            "refresh_token": acc.refresh_token,
            "access_token": acc.access_token,
            "token_expiry": acc.token_expiry.isoformat() if acc.token_expiry else None,
            "proxy_id": acc.proxy_id,
            "proxy_disabled": acc.proxy_disabled,
            "disabled_reason": acc.disabled_reason,
            "validation_blocked": acc.validation_blocked,
            "protected_models": json.loads(acc.protected_models) if acc.protected_models else [],
            "quota_data": acc.quota_data,
            "created_at": acc.created_at.isoformat(),
        }
        for acc in accounts
    ]


# Fingerprint functions
async def get_or_create_fingerprint(
    db: AsyncSession,
    account_id: int,
    user_agent: str | None = None,
    accept_language: str | None = None,
    platform: str | None = None,
    data: str | None = None,
    machine_id: str | None = None,
    mac_machine_id: str | None = None,
    dev_device_id: str | None = None,
    sqm_id: str | None = None,
) -> DeviceFingerprint:
    """Get or create a fingerprint for an account."""
    query = select(DeviceFingerprint).where(DeviceFingerprint.account_id == account_id)
    result = await db.execute(query)
    fingerprint = result.scalar_one_or_none()

    if fingerprint:
        # Update existing
        if user_agent is not None:
            fingerprint.user_agent = user_agent
        if accept_language is not None:
            fingerprint.accept_language = accept_language
        if platform is not None:
            fingerprint.platform = platform
        if data is not None:
            fingerprint.data = data
        if machine_id is not None:
            fingerprint.machine_id = machine_id
        if mac_machine_id is not None:
            fingerprint.mac_machine_id = mac_machine_id
        if dev_device_id is not None:
            fingerprint.dev_device_id = dev_device_id
        if sqm_id is not None:
            fingerprint.sqm_id = sqm_id
    else:
        # Create new
        fingerprint = DeviceFingerprint(
            account_id=account_id,
            user_agent=user_agent,
            accept_language=accept_language,
            platform=platform,
            data=data,
            machine_id=machine_id,
            mac_machine_id=mac_machine_id,
            dev_device_id=dev_device_id,
            sqm_id=sqm_id,
        )
        db.add(fingerprint)

    await db.commit()
    await db.refresh(fingerprint)
    return fingerprint


async def delete_fingerprint(db: AsyncSession, account_id: int) -> bool:
    """Delete a fingerprint for an account."""
    query = select(DeviceFingerprint).where(DeviceFingerprint.account_id == account_id)
    result = await db.execute(query)
    fingerprint = result.scalar_one_or_none()

    if fingerprint:
        await db.delete(fingerprint)
        await db.commit()
        return True
    return False


async def save_fingerprint_version(
    db: AsyncSession,
    account_id: int,
    label: str | None = None,
) -> DeviceFingerprintVersion:
    """Save current fingerprint as a version."""
    # Get current fingerprint
    fp_query = select(DeviceFingerprint).where(DeviceFingerprint.account_id == account_id)
    result = await db.execute(fp_query)
    fingerprint = result.scalar_one_or_none()

    if not fingerprint:
        raise ValueError("No fingerprint found")

    # Mark current as not current
    await db.execute(
        update(DeviceFingerprintVersion)
        .where(DeviceFingerprintVersion.account_id == account_id)
        .values(is_current=False)
    )

    # Create new version
    version = DeviceFingerprintVersion(
        account_id=account_id,
        label=label or f"Version {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        machine_id=fingerprint.machine_id,
        mac_machine_id=fingerprint.mac_machine_id,
        dev_device_id=fingerprint.dev_device_id,
        sqm_id=fingerprint.sqm_id,
        data=fingerprint.data,
        is_current=True,
    )
    db.add(version)
    await db.commit()
    await db.refresh(version)
    return version


async def get_fingerprint_versions(
    db: AsyncSession,
    account_id: int,
) -> list[DeviceFingerprintVersion]:
    """Get all fingerprint versions for an account."""
    query = (
        select(DeviceFingerprintVersion)
        .where(DeviceFingerprintVersion.account_id == account_id)
        .order_by(DeviceFingerprintVersion.created_at.desc())
    )
    result = await db.execute(query)
    return list(result.scalars().all())


async def restore_fingerprint_version(
    db: AsyncSession,
    account_id: int,
    version_id: int,
) -> DeviceFingerprint:
    """Restore a fingerprint from version."""
    # Get version
    version_query = select(DeviceFingerprintVersion).where(
        DeviceFingerprintVersion.id == version_id,
        DeviceFingerprintVersion.account_id == account_id,
    )
    result = await db.execute(version_query)
    version = result.scalar_one_or_none()

    if not version:
        raise ValueError("Version not found")

    # Get or create current fingerprint
    fp = await get_or_create_fingerprint(
        db,
        account_id,
        machine_id=version.machine_id,
        mac_machine_id=version.mac_machine_id,
        dev_device_id=version.dev_device_id,
        sqm_id=version.sqm_id,
        data=version.data,
    )

    # Mark version as current
    await db.execute(
        update(DeviceFingerprintVersion)
        .where(DeviceFingerprintVersion.account_id == account_id)
        .values(is_current=False)
    )
    version.is_current = True
    await db.commit()

    return fp


async def delete_fingerprint_version(
    db: AsyncSession,
    account_id: int,
    version_id: int,
) -> bool:
    """Delete a fingerprint version."""
    query = select(DeviceFingerprintVersion).where(
        DeviceFingerprintVersion.id == version_id,
        DeviceFingerprintVersion.account_id == account_id,
    )
    result = await db.execute(query)
    version = result.scalar_one_or_none()

    if version:
        await db.delete(version)
        await db.commit()
        return True
    return False
