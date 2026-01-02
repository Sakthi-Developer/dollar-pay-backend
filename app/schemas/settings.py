from pydantic import BaseModel
from decimal import Decimal
from typing import Optional


class PlatformSettings(BaseModel):
    usdt_to_inr_rate: Decimal = Decimal("85.00")
    platform_fee_percent: Decimal = Decimal("2.00")
    bonus_percent: Decimal = Decimal("0.00")
    inr_bonus_ratio: Decimal = Decimal("1.00")
    commission_percent: Decimal = Decimal("0.00")
    min_deposit_usdt: Decimal = Decimal("10.00")
    max_deposit_usdt: Decimal = Decimal("10000.00")
    min_withdrawal_inr: Decimal = Decimal("100.00")
    max_withdrawal_inr: Decimal = Decimal("100000.00")
    telegram_support_url: str = ""
    trc20_wallet_address: str = ""
    erc20_wallet_address: str = ""


class SettingUpdate(BaseModel):
    setting_key: str
    setting_value: str
    data_type: str = "string"
    description: Optional[str] = None
