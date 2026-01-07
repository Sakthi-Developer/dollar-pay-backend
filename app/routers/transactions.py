from fastapi import APIRouter, Depends, Form, HTTPException
from typing import List, Optional
from decimal import Decimal
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.core.security import get_current_user, get_current_admin
from app.schemas.transaction import TransactionResponse, TransactionDetail, AdminTransactionApproval, PaginatedTransactionResponse, TransactionUserInfo, UPIPayoutCreate, AdminUPIPayoutCreate, TransactionStatus
from app.schemas.settings import SettingUpdate
from app.services.transaction_service import transaction_service
from app.models.transaction import Transaction
from app.models.settings import PlatformSetting
from app.models.user import User
from datetime import datetime

router = APIRouter()

@router.post("/transactions/deposit", response_model=TransactionResponse)
def create_deposit_transaction(
    crypto_network: str = Form(...),
    crypto_amount: Decimal = Form(...),
    crypto_tx_hash: str = Form(...),
    user_notes: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a deposit transaction with crypto transaction hash."""
    return transaction_service.create_deposit(
        db=db,
        user_id=current_user['id'],
        crypto_network=crypto_network,
        crypto_amount=crypto_amount,
        crypto_tx_hash=crypto_tx_hash,
        user_notes=user_notes
    )

@router.post("/transactions/upi-payout", response_model=TransactionResponse)
def create_upi_payout_request(
    user_phone: str = Form(...),
    upi_amount: Decimal = Form(...),
    payment_reference: str = Form(...),
    crypto_amount: Decimal = Form(...),
    remaining_crypto: Decimal = Form(...),
    crypto_network: str = Form(...),
    user_notes: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a UPI payout request for a user by phone number with payment reference, crypto amount, and remaining crypto."""
    return transaction_service.create_upi_payout(
        db=db,
        user_phone=user_phone,
        upi_amount=upi_amount,
        payment_reference=payment_reference,
        crypto_amount=crypto_amount,
        remaining_crypto=remaining_crypto,
        crypto_network=crypto_network,
        user_notes=user_notes
    )

@router.get("/transactions/my-transactions", response_model=List[TransactionResponse])
def get_user_transactions(
    limit: int = 20,
    offset: int = 0,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get user's transactions."""
    transactions = db.query(Transaction).filter_by(user_id=current_user['id']).order_by(Transaction.created_at.desc()).limit(limit).offset(offset).all()

    # Create response objects with user data (current user)
    user = db.query(User).filter_by(id=current_user['id']).first()
    user_data = TransactionUserInfo.from_orm(user)

    transaction_responses = []
    for transaction in transactions:
        transaction_dict = TransactionResponse.from_orm(transaction).dict()
        transaction_dict['user'] = user_data.dict()
        transaction_responses.append(TransactionResponse(**transaction_dict))

    return transaction_responses

@router.get("/transactions/balance", response_model=dict)
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

@router.get("/transactions/{transaction_id}", response_model=TransactionDetail)
def get_transaction_detail(
    transaction_id: int,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get transaction details."""
    transaction = db.query(Transaction).filter_by(id=transaction_id, user_id=current_user['id']).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Create response with user data (current user)
    user = db.query(User).filter_by(id=current_user['id']).first()
    user_data = TransactionUserInfo.from_orm(user)
    transaction_dict = TransactionDetail.from_orm(transaction).dict()
    transaction_dict['user'] = user_data.dict()
    return TransactionDetail(**transaction_dict)

# Admin endpoints

@router.get("/admin/transactions/pending", response_model=List[TransactionResponse])
def get_pending_transactions(
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all pending transactions for admin review."""
    transactions = db.query(Transaction).join(User, Transaction.user_id == User.id).filter(Transaction.status == 'pending').order_by(Transaction.created_at.desc()).all()

    # Create response objects with user data
    transaction_responses = []
    for transaction in transactions:
        user_data = TransactionUserInfo.from_orm(transaction.user)
        transaction_dict = TransactionResponse.from_orm(transaction).dict()
        transaction_dict['user'] = user_data.dict()
        transaction_responses.append(TransactionResponse(**transaction_dict))

    return transaction_responses

@router.get("/admin/transactions", response_model=PaginatedTransactionResponse)
def get_all_transactions(
    status: Optional[str] = None,
    type: Optional[str] = None,
    page: int = 1,
    limit: int = 20,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all transactions for admin review with pagination."""
    query = db.query(Transaction).join(User, Transaction.user_id == User.id)
    if status:
        query = query.filter(Transaction.status == status)
    if type:
        query = query.filter(Transaction.type == type)

    total = query.count()
    transactions = query.order_by(Transaction.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    # Create response objects with user data
    transaction_responses = []
    for transaction in transactions:
        # Get user data
        user_data = TransactionUserInfo.from_orm(transaction.user)
        # Create transaction response with user
        transaction_dict = TransactionResponse.from_orm(transaction).dict()
        transaction_dict['user'] = user_data.dict()
        transaction_responses.append(TransactionResponse(**transaction_dict))

    return PaginatedTransactionResponse(
        transactions=transaction_responses,
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit
    )

@router.get("/admin/transactions/search-by-mobile", response_model=PaginatedTransactionResponse)
def search_transactions_by_mobile(
    mobile_number: str,
    page: int = 1,
    limit: int = 20,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Search transactions by user's mobile number with pagination."""
    query = db.query(Transaction).join(User, Transaction.user_id == User.id).filter(User.phone_number == mobile_number)
    total = query.count()
    transactions = query.order_by(Transaction.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    # Create response objects with user data
    transaction_responses = []
    for transaction in transactions:
        user_data = TransactionUserInfo.from_orm(transaction.user)
        transaction_dict = TransactionResponse.from_orm(transaction).dict()
        transaction_dict['user'] = user_data.dict()
        transaction_responses.append(TransactionResponse(**transaction_dict))

    return PaginatedTransactionResponse(
        transactions=transaction_responses,
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit
    )

@router.get("/admin/transactions/{transaction_id}", response_model=TransactionDetail)
def get_admin_transaction_detail(
    transaction_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get transaction details for admin."""
    transaction = db.query(Transaction).join(User, Transaction.user_id == User.id).filter(Transaction.id == transaction_id).first()
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Create response with user data
    user_data = TransactionUserInfo.from_orm(transaction.user)
    transaction_dict = TransactionDetail.from_orm(transaction).dict()
    transaction_dict['user'] = user_data.dict()
    return TransactionDetail(**transaction_dict)

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

@router.put("/admin/transactions/{transaction_id}/approve", response_model=dict)
def approve_transaction(
    transaction_id: int,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin approve transaction."""
    transaction_service.review_transaction(
        db=db,
        transaction_id=transaction_id,
        admin_id=current_admin['id'],
        status=TransactionStatus.APPROVED
    )
    return {"message": "Transaction approved successfully"}

@router.post("/admin/transactions/upi-payout", response_model=TransactionResponse)
def create_admin_upi_payout(
    payout: AdminUPIPayoutCreate,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Admin create UPI payout transaction for a user."""
    # Find user by phone number
    user = db.query(User).filter_by(phone_number=payout.user_phone).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found with the provided phone number")
    
    return transaction_service.create_admin_upi_payout(
        db=db,
        user_id=user.id,
        upi_amount=payout.upi_amount,
        payment_reference=payout.payment_reference,
        crypto_amount=payout.crypto_amount,
        remaining_crypto=payout.remaining_crypto,
        crypto_network=payout.crypto_network,
        user_notes=payout.user_notes,
        admin_notes=payout.admin_notes
    )

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
