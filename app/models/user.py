from sqlalchemy import Column, String, Boolean, DateTime, DECIMAL, BigInteger, ForeignKey, text
from sqlalchemy.orm import relationship
from app.models.base import Base

class User(Base):
    __tablename__ = 'users'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    phone_number = Column(String(15), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    referral_code = Column(String(20), unique=True, nullable=False)
    referred_by_code = Column(String(20), nullable=True)
    referred_by_user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)

    # Profile
    name = Column(String(100))
    email = Column(String(100))

    # Balance
    wallet_balance = Column(DECIMAL(15, 2), default=0.00)
    total_deposited = Column(DECIMAL(15, 2), default=0.00)
    total_withdrawn = Column(DECIMAL(15, 2), default=0.00)
    total_commission_earned = Column(DECIMAL(15, 2), default=0.00)
    total_usd_sent = Column(DECIMAL(15, 2), default=0.00)

    # UPI Details
    upi_id = Column(String(100))
    upi_holder_name = Column(String(100))
    bank_name = Column(String(100))
    is_upi_bound = Column(Boolean, default=False)

    # Bank Account Details (IMPS)
    account_number = Column(String(50))
    ifsc_code = Column(String(20))
    account_holder_name = Column(String(100))
    is_bank_bound = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    referrer = relationship("User", remote_side=[id], backref="referred_users")
    team_members = relationship("TeamMember", foreign_keys="TeamMember.parent_user_id", back_populates="parent")
    child_team_members = relationship("TeamMember", foreign_keys="TeamMember.child_user_id", back_populates="child")
    transactions = relationship("Transaction", back_populates="user")
    commissions_earned = relationship("Commission", foreign_keys="Commission.referrer_user_id", back_populates="referrer")
    commissions_received = relationship("Commission", foreign_keys="Commission.referred_user_id", back_populates="referred")
    activity_logs = relationship("ActivityLog", back_populates="user")
    notifications = relationship("Notification", back_populates="user")
