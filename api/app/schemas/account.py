import json
from datetime import datetime

from pydantic import BaseModel, EmailStr

from app.models import AccountStatus, AccountTier


# Model Quota Schemas
class ModelQuota(BaseModel):
    name: str
    percentage: float = 0
    reset_time: str | None = None
    display_name: str | None = None
    supports_images: bool = False
    supports_thinking: bool = False
    thinking_budget: int | None = None
    recommended: bool = False
    max_tokens: int | None = None
    max_output_tokens: int | None = None


class QuotaData(BaseModel):
    models: list[ModelQuota] = []
    last_updated: datetime | None = None
    is_forbidden: bool = False
    forbidden_reason: str | None = None
    subscription_tier: str | None = None
    model_forwarding_rules: dict[str, str] = {}


# Device Fingerprint Schemas
class FingerprintCreate(BaseModel):
    user_agent: str | None = None
    accept_language: str | None = None
    platform: str | None = None
    data: str | None = None
    machine_id: str | None = None
    mac_machine_id: str | None = None
    dev_device_id: str | None = None
    sqm_id: str | None = None


class FingerprintResponse(BaseModel):
    id: int
    account_id: int
    machine_id: str | None = None
    mac_machine_id: str | None = None
    dev_device_id: str | None = None
    sqm_id: str | None = None
    user_agent: str | None = None
    accept_language: str | None = None
    platform: str | None = None
    data: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class FingerprintVersionResponse(BaseModel):
    id: int
    account_id: int
    label: str | None = None
    machine_id: str | None = None
    mac_machine_id: str | None = None
    dev_device_id: str | None = None
    sqm_id: str | None = None
    data: str | None = None
    is_current: bool = False
    created_at: datetime

    model_config = {"from_attributes": True}


# Account Schemas
class AccountCreate(BaseModel):
    email: EmailStr
    name: str | None = None
    label: str | None = None
    custom_label: str | None = None
    tier: AccountTier = AccountTier.free
    refresh_token: str | None = None
    access_token: str | None = None
    token_expiry: datetime | None = None
    proxy_id: int | None = None


class AccountUpdate(BaseModel):
    name: str | None = None
    label: str | None = None
    custom_label: str | None = None
    tier: AccountTier | None = None
    status: AccountStatus | None = None
    proxy_id: int | None = None


class AccountResponse(BaseModel):
    id: int
    email: str
    name: str | None = None
    label: str | None = None
    custom_label: str | None = None
    tier: AccountTier
    status: AccountStatus
    is_current: bool = False
    sort_order: int = 0
    token_expiry: datetime | None = None
    proxy_id: int | None = None
    proxy_disabled: bool = False
    proxy_disabled_reason: str | None = None
    disabled_reason: str | None = None
    validation_blocked: bool = False
    validation_blocked_until: datetime | None = None
    validation_blocked_reason: str | None = None
    validation_url: str | None = None
    protected_models: list[str] = []
    quota: QuotaData | None = None
    last_used: datetime | None = None
    created_at: datetime
    updated_at: datetime
    fingerprint: FingerprintResponse | None = None

    model_config = {"from_attributes": True}

    @classmethod
    def model_validate(cls, obj, **kwargs):
        # Handle quota_data JSON parsing
        if hasattr(obj, "quota_data") and obj.quota_data:
            try:
                quota_dict = json.loads(obj.quota_data)
                obj.quota = QuotaData(**quota_dict)
            except Exception:
                obj.quota = None

        # Handle protected_models JSON parsing
        if hasattr(obj, "protected_models"):
            if obj.protected_models:
                try:
                    obj.protected_models = json.loads(obj.protected_models)
                except Exception:
                    obj.protected_models = []
            else:
                obj.protected_models = []

        return super().model_validate(obj, **kwargs)


class AccountList(BaseModel):
    items: list[AccountResponse]
    total: int
    page: int
    page_size: int


class CurrentAccountResponse(BaseModel):
    account: AccountResponse | None = None


# Batch Operations
class BatchIdsRequest(BaseModel):
    account_ids: list[int]


class BatchDeleteResponse(BaseModel):
    deleted: int
    total: int


class BatchRefreshResponse(BaseModel):
    refreshed: int
    failed: int
    total: int


# Import/Export
class ImportRequest(BaseModel):
    accounts: list[dict]


class ImportResponse(BaseModel):
    imported: int
    total: int


class ExportResponse(BaseModel):
    accounts: list[dict]


# Reorder
class ReorderRequest(BaseModel):
    account_ids: list[int]


# Toggle Proxy
class ToggleProxyRequest(BaseModel):
    enabled: bool
    reason: str | None = None


# Warmup
class WarmupResponse(BaseModel):
    account_id: int
    status: str
    message: str


# Switch Account
class SwitchAccountResponse(BaseModel):
    account_id: int
    message: str
