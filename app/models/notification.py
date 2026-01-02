from sqlalchemy import Column, String, Boolean, DateTime, Text, BigInteger, ForeignKey, CheckConstraint, text
from sqlalchemy.orm import relationship
from app.models.base import Base

class Notification(Base):
    __tablename__ = 'notifications'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)

    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    type = Column(String(20), default='info')

    is_read = Column(Boolean, default=False)
    read_at = Column(DateTime, nullable=True)

    related_transaction_id = Column(BigInteger, ForeignKey('transactions.id'), nullable=True)

    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    user = relationship("User", back_populates="notifications")
    transaction = relationship("Transaction", back_populates="notifications")

    __table_args__ = (
        CheckConstraint("type IN ('info', 'success', 'warning', 'transaction')"),
    )
