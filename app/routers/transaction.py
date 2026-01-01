from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
import uuid
import boto3
from botocore.exceptions import NoCredentialsError
from app.models.transaction import DepositCreate, TransactionResponse, TransactionDetail
from app.models.settings import PlatformSettings
from app.db.database import get_db_context
from app.db.models import Transaction, PlatformSetting, User
from app.core.security import get_current_user, get_current_admin
from app.core.config import settings
from decimal import Decimal

router = APIRouter(prefix="/transaction", tags=["Transaction"])


def upload_to_s3(file: UploadFile, filename: str) -> str:
    """Upload file to S3 and return the URL."""
    try:
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.aws_access_key_id,
            aws_secret_access_key=settings.aws_secret_access_key,
            region_name=settings.aws_region
        )
        
        # Upload file
        s3_client.upload_fileobj(file.file, settings.s3_bucket_name, filename)
        
        # Generate URL
        url = f"https://{settings.s3_bucket_name}.s3.{settings.aws_region}.amazonaws.com/{filename}"
        return url
    except NoCredentialsError:
        raise HTTPException(status_code=500, detail="AWS credentials not available")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to upload file: {str(e)}")


def get_platform_settings(db) -> PlatformSettings:
    """Get current platform settings."""
    settings_dict = {}
    settings_rows = db.query(PlatformSetting).all()
    for setting in settings_rows:
        if setting.data_type == 'number':
            settings_dict[setting.setting_key] = Decimal(setting.setting_value)
        else:
            settings_dict[setting.setting_key] = setting.setting_value
    
    return PlatformSettings(**settings_dict)


@router.post("/deposit", response_model=TransactionResponse)
def create_deposit_transaction(
    crypto_network: str = Form(...),
    crypto_amount: Decimal = Form(...),
    crypto_tx_hash: Optional[str] = Form(None),
    user_notes: Optional[str] = Form(None),
    screenshot: UploadFile = File(...),
    current_user: dict = Depends(get_current_user)
):
    """Create a deposit transaction with screenshot upload."""
    
    # Validate file type
    if not screenshot.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Generate unique filename
    file_extension = screenshot.filename.split('.')[-1] if '.' in screenshot.filename else 'jpg'
    filename = f"screenshots/{current_user['id']}/{uuid.uuid4()}.{file_extension}"
    
    with get_db_context() as db:
        # Get platform settings
        platform_settings = get_platform_settings(db)
        
        # Validate amount limits
        if crypto_amount < platform_settings.min_deposit_usdt:
            raise HTTPException(status_code=400, detail=f"Minimum deposit is {platform_settings.min_deposit_usdt} USDT")
        if crypto_amount > platform_settings.max_deposit_usdt:
            raise HTTPException(status_code=400, detail=f"Maximum deposit is {platform_settings.max_deposit_usdt} USDT")
        
        # Upload screenshot to S3
        screenshot_url = upload_to_s3(screenshot, filename)
        
        # Calculate amounts
        exchange_rate = platform_settings.usdt_to_inr_rate
        gross_inr = crypto_amount * exchange_rate
        platform_fee = gross_inr * (platform_settings.platform_fee_percent / 100)
        bonus = gross_inr * (platform_settings.bonus_percent / 100)
        net_inr = gross_inr - platform_fee + bonus
        
        # Get user's UPI details
        user = db.query(User).filter_by(id=current_user['id']).first()
        if not user or not user.is_upi_bound:
            raise HTTPException(status_code=400, detail="UPI details not bound")
        
        # Create transaction
        transaction_uid = f"DEP{uuid.uuid4().hex[:8].upper()}"
        transaction = Transaction(
            transaction_uid=transaction_uid,
            user_id=current_user['id'],
            type='deposit',
            status='pending',
            crypto_network=crypto_network.upper(),
            crypto_amount=crypto_amount,
            crypto_tx_hash=crypto_tx_hash,
            screenshot_url=screenshot_url,
            user_notes=user_notes,
            exchange_rate=exchange_rate,
            platform_fee_percent=platform_settings.platform_fee_percent,
            platform_fee_amount=platform_fee,
            bonus_percent=platform_settings.bonus_percent,
            bonus_amount=bonus,
            gross_inr_amount=gross_inr,
            net_inr_amount=net_inr,
            user_upi_id=user.upi_id,
            user_bank_name=user.bank_name
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        return TransactionResponse.from_orm(transaction)


@router.get("/my-transactions", response_model=List[TransactionResponse])
def get_user_transactions(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user)
):
    """Get user's transactions."""
    with get_db_context() as db:
        transactions = db.query(Transaction).filter_by(user_id=current_user['id']).order_by(Transaction.created_at.desc()).limit(limit).offset(offset).all()
        return [TransactionResponse.from_orm(t) for t in transactions]


@router.get("/{transaction_id}", response_model=TransactionDetail)
def get_transaction_detail(
    transaction_id: int,
    current_user: dict = Depends(get_current_user)
):
    """Get transaction details."""
    with get_db_context() as db:
        transaction = db.query(Transaction).filter_by(id=transaction_id, user_id=current_user['id']).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        return TransactionDetail.from_orm(transaction)


# Admin endpoints
class SettingUpdate(BaseModel):
    setting_key: str
    setting_value: str
    data_type: str = "string"
    description: Optional[str] = None


@router.put("/admin/settings", response_model=dict)
def update_platform_setting(
    setting: SettingUpdate,
    current_admin: dict = Depends(get_current_admin)
):
    """Update platform setting (Admin only)."""
    with get_db_context() as db:
        # Check if setting exists
        existing_setting = db.query(PlatformSetting).filter_by(setting_key=setting.setting_key).first()
        
        if existing_setting:
            existing_setting.setting_value = setting.setting_value
            existing_setting.data_type = setting.data_type
            if setting.description:
                existing_setting.description = setting.description
            existing_setting.updated_by_admin_id = current_admin['id']
            existing_setting.updated_at = datetime.utcnow()
        else:
            new_setting = PlatformSetting(
                setting_key=setting.setting_key,
                setting_value=setting.setting_value,
                data_type=setting.data_type,
                description=setting.description,
                updated_by_admin_id=current_admin['id']
            )
            db.add(new_setting)
        
        db.commit()
        return {"message": "Setting updated successfully"}


@router.get("/admin/settings", response_model=List[dict])
def get_all_platform_settings(current_admin: dict = Depends(get_current_admin)):
    """Get all platform settings (Admin only)."""
    with get_db_context() as db:
        settings = db.query(PlatformSetting).all()
        return [
            {
                "id": s.id,
                "setting_key": s.setting_key,
                "setting_value": s.setting_value,
                "data_type": s.data_type,
                "description": s.description,
                "updated_by_admin_id": s.updated_by_admin_id,
                "updated_at": s.updated_at
            }
            for s in settings
        ]