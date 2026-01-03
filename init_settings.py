#!/usr/bin/env python3
"""
Script to initialize platform settings in the database.
"""
from app.db.database import get_db_context
from app.models.settings import PlatformSetting

def init_platform_settings():
    """Initialize default platform settings."""
    settings_data = [
        {
            "setting_key": "usdt_to_inr_rate",
            "setting_value": "98.94",
            "data_type": "number",
            "description": "Current USDT to INR exchange rate"
        },
        {
            "setting_key": "platform_fee_percent",
            "setting_value": "2",
            "data_type": "number",
            "description": "Platform fee percentage on deposits"
        },
        {
            "setting_key": "bonus_percent",
            "setting_value": "2",
            "data_type": "number",
            "description": "Bonus percentage on deposits"
        },
        {
            "setting_key": "inr_bonus_ratio",
            "setting_value": "4",
            "data_type": "number",
            "description": "INR deposit bonus ratio"
        },
        {
            "setting_key": "commission_percent",
            "setting_value": "1",
            "data_type": "number",
            "description": "Referral commission percentage"
        },
        {
            "setting_key": "min_deposit_usdt",
            "setting_value": "10",
            "data_type": "number",
            "description": "Minimum deposit amount in USDT"
        },
        {
            "setting_key": "max_deposit_usdt",
            "setting_value": "10000",
            "data_type": "number",
            "description": "Maximum deposit amount in USDT"
        },
        {
            "setting_key": "telegram_support_url",
            "setting_value": "https://t.me/dollarpay_support",
            "data_type": "string",
            "description": "Telegram support link"
        },
        {
            "setting_key": "trc20_wallet_address",
            "setting_value": "",
            "data_type": "string",
            "description": "TRC-20 USDT wallet address"
        },
        {
            "setting_key": "erc20_wallet_address",
            "setting_value": "",
            "data_type": "string",
            "description": "ERC-20 USDT wallet address"
        }
    ]

    with get_db_context() as db:
        for setting_data in settings_data:
            # Check if setting already exists
            existing = db.query(PlatformSetting).filter_by(setting_key=setting_data["setting_key"]).first()
            if not existing:
                setting = PlatformSetting(**setting_data)
                db.add(setting)
                print(f"Added setting: {setting_data['setting_key']}")
            else:
                print(f"Setting already exists: {setting_data['setting_key']}")
        
        db.commit()
        print("Platform settings initialization completed.")

if __name__ == "__main__":
    init_platform_settings()