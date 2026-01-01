from sqlalchemy import Column, String, DateTime, DECIMAL, Text, BigInteger, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    transaction_uid = Column(String(50), unique=True, nullable=False)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    type = Column(String(20), nullable=False)
    status = Column(String(20), default='pending')

    crypto_network = Column(String(20))
    crypto_wallet_address = Column(String(100))
    crypto_amount = Column(DECIMAL(15, 6))
    crypto_tx_hash = Column(String(100))

    screenshot_url = Column(String(500))
    user_notes = Column(Text)

    exchange_rate = Column(DECIMAL(10, 2))
    platform_fee_percent = Column(DECIMAL(5, 2))
    platform_fee_amount = Column(DECIMAL(15, 2))
    bonus_percent = Column(DECIMAL(5, 2), default=0)
    bonus_amount = Column(DECIMAL(15, 2), default=0)
    gross_inr_amount = Column(DECIMAL(15, 2))
    net_inr_amount = Column(DECIMAL(15, 2))

    user_upi_id = Column(String(100))
    user_bank_name = Column(String(100))

    admin_id = Column(BigInteger, ForeignKey('admins.id'), nullable=True)
    admin_reviewed_at = Column(DateTime, nullable=True)
    admin_notes = Column(Text)
    rejection_reason = Column(Text)

    payment_reference = Column(String(100))
    payment_completed_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default='CURRENT_TIMESTAMP')
    updated_at = Column(DateTime, default='CURRENT_TIMESTAMP')

    # Relationships
    user = relationship("User", back_populates="transactions")
    admin = relationship("Admin", back_populates="transactions_reviewed")
    commissions = relationship("Commission", back_populates="transaction")
    notifications = relationship("Notification", back_populates="transaction")

    __table_args__ = (
        CheckConstraint("type IN ('crypto_deposit', 'upi_payout', 'withdrawal', 'commission')"),
        CheckConstraint("status IN ('pending', 'processing', 'approved', 'rejected', 'completed', 'failed')"),
    )
