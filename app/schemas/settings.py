from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class PlatformSettings(BaseModel):
    usdt_to_inr_rate: Decimal
    platform_fee_percent: Decimal
    bonus_percent: Decimal
    inr_bonus_ratio: Decimal
    commission_percent: Decimal
    min_deposit_usdt: Decimal
    max_deposit_usdt: Decimal
    min_withdrawal_inr: Decimal
    max_withdrawal_inr: Decimal
    telegram_support_url: str
    trc20_wallet_address: str
    erc20_wallet_address: str


class SettingUpdate(BaseModel):
    setting_key: str
    setting_value: str
    data_type: str = "string"
    description: Optional[str] = None
