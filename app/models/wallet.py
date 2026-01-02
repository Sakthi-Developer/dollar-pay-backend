from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, ForeignKey, text
from sqlalchemy.orm import relationship
from app.models.base import Base

class CryptoWallet(Base):
    __tablename__ = 'crypto_wallets'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    network_type = Column(String(20), nullable=False)
    wallet_address = Column(String(100), unique=True, nullable=False)
    currency = Column(String(10), default='USDT')
    is_active = Column(Boolean, default=True)
    assigned_to_user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
