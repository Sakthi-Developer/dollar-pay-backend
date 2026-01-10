import json
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.models.settings import PlatformSetting
from app.schemas.settings import TelegramLinksResponse, TelegramLink, BannerImagesResponse

router = APIRouter()


@router.get("/config/telegram-links", response_model=TelegramLinksResponse)
def get_telegram_links(db: Session = Depends(get_db)):
    """Get support Telegram links (promotion group and private support)."""
    setting = db.query(PlatformSetting).filter_by(setting_key="telegram_links").first()

    if not setting or not setting.setting_value:
        return TelegramLinksResponse(links=[])

    try:
        links_data = json.loads(setting.setting_value)
        links = [TelegramLink(**link) for link in links_data]
        return TelegramLinksResponse(links=links)
    except (json.JSONDecodeError, TypeError):
        return TelegramLinksResponse(links=[])


@router.get("/config/banners", response_model=BannerImagesResponse)
def get_home_banners(db: Session = Depends(get_db)):
    """Get list of banner images for the app home screen."""
    setting = db.query(PlatformSetting).filter_by(setting_key="home_banners").first()

    if not setting or not setting.setting_value:
        return BannerImagesResponse(banners=[])

    try:
        banners = json.loads(setting.setting_value)
        if isinstance(banners, list):
            return BannerImagesResponse(banners=banners)
        return BannerImagesResponse(banners=[])
    except (json.JSONDecodeError, TypeError):
        return BannerImagesResponse(banners=[])
