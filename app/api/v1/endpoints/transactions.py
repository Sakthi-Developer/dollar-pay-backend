from fastapi import APIRouter, Depends, Form, HTTPException
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.schemas.transaction import TransactionResponse, TransactionDetail, WithdrawalCreate, AdminTransactionApproval
from app.schemas.settings import SettingUpdate
from app.services.transaction_service import transaction_service
from app.models.transaction import Transaction
from app.models.settings import PlatformSetting
from app.models.user import User
from datetime import datetime

router = APIRouter()

@router.post("/deposit", response_model=TransactionResponse)
def create_deposit_transaction(
    crypto_network: str = Form(...),
    crypto_amount: Decimal = Form(...),
    crypto_tx_hash: Optional[str] = Form(None),
    user_notes: Optional[str] = Form(None),
    screenshot_url: str = Form(...),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a deposit transaction with screenshot URL."""
    return transaction_service.create_deposit(
        db=db,
        user_id=current_user['id'],
        crypto_network=crypto_network,
        crypto_amount=crypto_amount,
        screenshot_url=screenshot_url,
        crypto_tx_hash=crypto_tx_hash,
        user_notes=user_notes
    )

@router.post("/withdrawal", response_model=TransactionResponse)
def create_withdrawal_request(
    withdrawal: WithdrawalCreate,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a withdrawal request."""
    return transaction_service.create_withdrawal(
        db=db,
        user_id=current_user['id'],
        amount=withdrawal.amount
    )

@router.get("/my-transactions", response_model=List[TransactionResponse])
def get_user_transactions(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's transactions."""
    transactions = db.query(Transaction).filter_by(user_id=current_user['id']).order_by(Transaction.created_at.desc()).limit(limit).offset(offset).all()
    return [TransactionResponse.from_orm(t) for t in transactions]

@router.get("/balance", response_model=dict)
def get_user_balance(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's wallet balance and transaction summary."""
    user = db.query(User).filter_by(id=current_user['id']).first()
    return {
        "wallet_balance": user.wallet_balance,
        "total_deposited": user.total_deposited,
        "total_withdrawn": user.total_withdrawn,
        "total_commission_earned": user.total_commission_earned
    }

@router.get("/{transaction_id}", response_model=TransactionDetail)
def get_transaction_detail(
    transaction_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction details."""
    transaction = db.query(Transaction).filter_by(id=transaction_id, user_id=current_user['id']).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionDetail.from_orm(transaction)

# Admin endpoints

@router.get("/admin/pending", response_model=List[TransactionResponse])
def get_pending_transactions(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all pending transactions for admin review."""
    transactions = db.query(Transaction).filter_by(status='pending').order_by(Transaction.created_at.desc()).all()
    return [TransactionResponse.from_orm(t) for t in transactions]

@router.get("/admin/transactions", response_model=List[TransactionResponse])
def get_all_transactions(
    status: Optional[str] = None,
    type: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all transactions for admin review."""
    query = db.query(Transaction)
    if status:
        query = query.filter_by(status=status)
    if type:
        query = query.filter_by(type=type)
    transactions = query.order_by(Transaction.created_at.desc()).limit(limit).offset(offset).all()
    return [TransactionResponse.from_orm(t) for t in transactions]

@router.get("/admin/transactions/{transaction_id}", response_model=TransactionDetail)
def get_admin_transaction_detail(
    transaction_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get transaction details for admin."""
    transaction = db.query(Transaction).filter_by(id=transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return TransactionDetail.from_orm(transaction)

@router.put("/admin/transactions/{transaction_id}/review", response_model=dict)
def review_transaction(
    transaction_id: int,
    approval: AdminTransactionApproval,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin review transaction: approve or reject."""
    transaction_service.review_transaction(
        db=db,
        transaction_id=transaction_id,
        admin_id=current_admin['id'],
        status=approval.status,
        admin_notes=approval.admin_notes,
        rejection_reason=approval.rejection_reason,
        payment_reference=approval.payment_reference,
        transaction_fee=approval.transaction_fee,
        platform_fee=approval.platform_fee
    )
    return {"message": "Transaction reviewed successfully"}

@router.get("/admin/settings", response_model=List[dict])
def get_all_platform_settings(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all platform settings (Admin only)."""
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

@router.put("/admin/settings", response_model=dict)
def update_platform_setting(
    setting: SettingUpdate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Update platform setting (Admin only)."""
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
