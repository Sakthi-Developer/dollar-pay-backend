from sqlalchemy import Column, String, DateTime, DECIMAL, BigInteger, ForeignKey, CheckConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

class Commission(Base):
    __tablename__ = 'commissions'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    referrer_user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    referred_user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    transaction_id = Column(BigInteger, ForeignKey('transactions.id'), nullable=False)

    commission_percent = Column(DECIMAL(5, 2), nullable=False)
    base_amount = Column(DECIMAL(15, 2), nullable=False)
    commission_amount = Column(DECIMAL(15, 2), nullable=False)

    status = Column(String(20), default='pending')
    credited_at = Column(DateTime, nullable=True)

    created_at = Column(DateTime, default='CURRENT_TIMESTAMP')
    updated_at = Column(DateTime, default='CURRENT_TIMESTAMP')

    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_user_id], back_populates="commissions_earned")
    referred = relationship("User", foreign_keys=[referred_user_id], back_populates="commissions_received")
    transaction = relationship("Transaction", back_populates="commissions")

    __table_args__ = (
        CheckConstraint("status IN ('pending', 'credited', 'cancelled')"),
    )
