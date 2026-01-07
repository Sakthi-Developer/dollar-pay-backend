import uuid
from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionStatus
from app.services.storage_service import StorageService
from app.services.settings_service import settings_service
from app.services.notification_service import notification_service

class TransactionService:
    @staticmethod
    def create_deposit(
        db: Session,
        user_id: int,
        crypto_network: str,
        crypto_amount: Decimal,
        crypto_tx_hash: str,
        user_notes: Optional[str] = None
    ) -> Transaction:
        # Get platform settings
        platform_settings = settings_service.get_platform_settings(db)
        
        # Validate amount limits
        if crypto_amount < platform_settings.min_deposit_usdt:
            raise HTTPException(status_code=400, detail=f"Minimum deposit is {platform_settings.min_deposit_usdt} USDT")
        if crypto_amount > platform_settings.max_deposit_usdt:
            raise HTTPException(status_code=400, detail=f"Maximum deposit is {platform_settings.max_deposit_usdt} USDT")

        # Calculate amounts
        exchange_rate = platform_settings.usdt_to_inr_rate
        gross_inr = crypto_amount * exchange_rate
        platform_fee = gross_inr * (platform_settings.platform_fee_percent / 100)
        bonus = gross_inr * (platform_settings.bonus_percent / 100)
        net_inr = gross_inr - platform_fee + bonus
        
        # Get user's UPI details
        user = db.query(User).filter_by(id=user_id).first()
        if not user or not user.is_upi_bound:
            raise HTTPException(status_code=400, detail="UPI details not bound")
        
        # Create transaction
        transaction_uid = f"DEP{uuid.uuid4().hex[:8].upper()}"
        transaction = Transaction(
            transaction_uid=transaction_uid,
            user_id=user_id,
            type='crypto_deposit',
            status='pending',
            crypto_network=crypto_network.upper(),
            crypto_amount=crypto_amount,
            crypto_tx_hash=crypto_tx_hash,
            user_notes=user_notes,
            exchange_rate=exchange_rate,
            platform_fee_percent=platform_settings.platform_fee_percent,
            platform_fee_amount=platform_fee,
            bonus_percent=platform_settings.bonus_percent,
            bonus_amount=bonus,
            gross_inr_amount=gross_inr,
            net_inr_amount=net_inr,
            user_upi_id=user.upi_id,
            user_bank_name=user.bank_name,
            created_at=datetime.utcnow()
        )
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Notify admin
        notification_service.broadcast_to_admins_sync({
            "type": "new_transaction",
            "transaction_id": transaction.id,
            "transaction_uid": transaction.transaction_uid,
            "user_id": transaction.user_id,
            "transaction_type": transaction.type,
            "amount": float(transaction.crypto_amount),
            "network": transaction.crypto_network,
            "message": f"New crypto deposit request from user {user_id}"
        })
        
        return transaction

    @staticmethod
    def create_upi_payout(
        db: Session,
        user_phone: str,
        upi_amount: Decimal,
        payment_reference: str,
        crypto_amount: Decimal,
        remaining_crypto: Decimal,
        crypto_network: str,
        user_notes: Optional[str] = None
    ) -> Transaction:
        # Get platform settings
        platform_settings = settings_service.get_platform_settings(db)

        # Validate amount limits (using withdrawal limits for UPI payouts)
        if upi_amount < platform_settings.min_withdrawal_inr:
            raise HTTPException(status_code=400, detail=f"Minimum UPI payout is {platform_settings.min_withdrawal_inr} INR")
        if upi_amount > platform_settings.max_withdrawal_inr:
            raise HTTPException(status_code=400, detail=f"Maximum UPI payout is {platform_settings.max_withdrawal_inr} INR")

        # Find user by phone number
        user = db.query(User).filter_by(phone_number=user_phone).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found with the provided phone number")
        if not user.is_upi_bound:
            raise HTTPException(status_code=400, detail="UPI details not bound")
        
        # Calculate amounts
        gross_inr = upi_amount
        platform_fee = gross_inr * (platform_settings.platform_fee_percent / 100)
        bonus = gross_inr * (platform_settings.bonus_percent / 100)
        net_inr = gross_inr - platform_fee + bonus
        
        # Create UPI payout transaction
        transaction_uid = f"UPI{uuid.uuid4().hex[:8].upper()}"
        transaction = Transaction(
            transaction_uid=transaction_uid,
            user_id=user.id,
            type='upi_payout',
            status='pending',
            crypto_network=crypto_network.upper(),
            crypto_amount=crypto_amount,
            remaining_crypto=remaining_crypto,
            user_notes=user_notes,
            exchange_rate=Decimal('1.0'),
            platform_fee_percent=platform_settings.platform_fee_percent,
            platform_fee_amount=platform_fee,
            bonus_percent=platform_settings.bonus_percent,
            bonus_amount=bonus,
            gross_inr_amount=gross_inr,
            net_inr_amount=net_inr,
            user_upi_id=user.upi_id,
            user_bank_name=user.bank_name,
            payment_reference=payment_reference,
            created_at=datetime.utcnow()
        )

        # Update user's total_usd_sent
        user.total_usd_sent = (user.total_usd_sent or Decimal('0.00')) + crypto_amount
        
        db.add(transaction)
        db.commit()
        db.refresh(transaction)
        
        # Notify admin
        notification_service.broadcast_to_admins_sync({
            "type": "new_transaction",
            "transaction_id": transaction.id,
            "transaction_uid": transaction.transaction_uid,
            "user_id": transaction.user_id,
            "transaction_type": transaction.type,
            "amount": float(transaction.gross_inr_amount),
            "message": f"New UPI payout request from user {user.id} ({user_phone})"
        })
        
        return transaction

    @staticmethod
    def create_admin_upi_payout(
        db: Session,
        user_id: int,
        upi_amount: Decimal,
        payment_reference: str,
        crypto_amount: Decimal,
        remaining_crypto: Decimal,
        crypto_network: str,
        user_notes: Optional[str] = None,
        admin_notes: Optional[str] = None
    ) -> Transaction:
        # Get platform settings
        platform_settings = settings_service.get_platform_settings(db)
        
        # Validate amount limits (using withdrawal limits for UPI payouts)
        if upi_amount < platform_settings.min_withdrawal_inr:
            raise HTTPException(status_code=400, detail=f"Minimum UPI payout is {platform_settings.min_withdrawal_inr} INR")
        if upi_amount > platform_settings.max_withdrawal_inr:
            raise HTTPException(status_code=400, detail=f"Maximum UPI payout is {platform_settings.max_withdrawal_inr} INR")
        
        # Get user's UPI details
        user = db.query(User).filter_by(id=user_id).first()
        if not user or not user.is_upi_bound:
            raise HTTPException(status_code=400, detail="UPI details not bound")
        
        # Calculate amounts
        gross_inr = upi_amount
        platform_fee = gross_inr * (platform_settings.platform_fee_percent / 100)
        bonus = gross_inr * (platform_settings.bonus_percent / 100)
        net_inr = gross_inr - platform_fee + bonus
        
        # Create UPI payout transaction as completed
        transaction_uid = f"UPI{uuid.uuid4().hex[:8].upper()}"
        transaction = Transaction(
            transaction_uid=transaction_uid,
            user_id=user_id,
            type='upi_payout',
            status='completed',
            crypto_network=crypto_network.upper(),
            crypto_amount=crypto_amount,
            remaining_crypto=remaining_crypto,
            user_notes=user_notes,
            admin_notes=admin_notes,
            exchange_rate=Decimal('1.0'),
            platform_fee_percent=platform_settings.platform_fee_percent,
            platform_fee_amount=platform_fee,
            bonus_percent=platform_settings.bonus_percent,
            bonus_amount=bonus,
            gross_inr_amount=gross_inr,
            net_inr_amount=net_inr,
            user_upi_id=user.upi_id,
            user_bank_name=user.bank_name,
            payment_reference=payment_reference,
            payment_completed_at=datetime.utcnow(),
            created_at=datetime.utcnow()
        )

        db.add(transaction)

        # Credit user balance
        user.wallet_balance += net_inr
        user.total_deposited += net_inr  # Assuming payouts are treated as deposits for balance

        # Update user's total_usd_sent
        user.total_usd_sent = (user.total_usd_sent or Decimal('0.00')) + crypto_amount
        
        db.commit()
        db.refresh(transaction)
        
        return transaction

    @staticmethod
    def review_transaction(
        db: Session,
        transaction_id: int,
        admin_id: int,
        status: TransactionStatus,
        admin_notes: Optional[str] = None,
        rejection_reason: Optional[str] = None,
        payment_reference: Optional[str] = None,
        transaction_fee: Optional[Decimal] = None,
        platform_fee: Optional[Decimal] = None
    ) -> Transaction:
        transaction = db.query(Transaction).filter_by(id=transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        if transaction.status != 'pending':
            raise HTTPException(status_code=400, detail="Transaction already reviewed")
        
        transaction.status = status.value
        transaction.admin_id = admin_id
        transaction.admin_reviewed_at = datetime.utcnow()
        transaction.admin_notes = admin_notes
        
        if status == TransactionStatus.REJECTED:
            transaction.rejection_reason = rejection_reason
        elif status == TransactionStatus.APPROVED:
            # For crypto_deposit, create UPI payout transaction
            if transaction.type == 'crypto_deposit':
                # Update user balance
                user = transaction.user
                user.total_deposited += transaction.net_inr_amount
                user.wallet_balance += transaction.net_inr_amount
                
                # Create UPI payout transaction
                payout_uid = f"PAY{uuid.uuid4().hex[:8].upper()}"
                payout_transaction = Transaction(
                    transaction_uid=payout_uid,
                    user_id=transaction.user_id,
                    type='upi_payout',
                    status='completed',
                    gross_inr_amount=transaction.net_inr_amount,
                    net_inr_amount=transaction.net_inr_amount - (transaction_fee or 0) - (platform_fee or 0),
                    platform_fee_amount=transaction_fee or 0,  # Use platform_fee_amount for transaction fee
                    user_upi_id=transaction.user_upi_id,
                    user_bank_name=transaction.user_bank_name,
                    payment_reference=payment_reference,
                    admin_id=admin_id,
                    payment_completed_at=datetime.utcnow(),
                    created_at=datetime.utcnow()
                )
                db.add(payout_transaction)
            elif transaction.type == 'withdrawal':
                # For withdrawal, debit user balance
                user = transaction.user
                if user.wallet_balance < transaction.gross_inr_amount:
                    raise HTTPException(status_code=400, detail="Insufficient balance")
                user.wallet_balance -= transaction.gross_inr_amount
                user.total_withdrawn += transaction.gross_inr_amount
                transaction.payment_reference = payment_reference
                transaction.payment_completed_at = datetime.utcnow()
        
        db.commit()
        return transaction

transaction_service = TransactionService()
