from sqlalchemy.orm import Session
from app.models.settings import PlatformSetting
from app.schemas.settings import PlatformSettings
from decimal import Decimal

class SettingsService:
    @staticmethod
    def get_platform_settings(db: Session) -> PlatformSettings:
        """Get current platform settings."""
        settings_dict = {}
        settings_rows = db.query(PlatformSetting).all()
        for setting in settings_rows:
            if setting.data_type == 'number':
                settings_dict[setting.setting_key] = Decimal(setting.setting_value)
            else:
                settings_dict[setting.setting_key] = setting.setting_value
        
        return PlatformSettings(**settings_dict)

settings_service = SettingsService()
