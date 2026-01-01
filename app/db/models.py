from sqlalchemy import create_engine, Column, Integer, String, Boolean, DateTime, DECIMAL, Text, BigInteger, ForeignKey, JSON, UniqueConstraint, Index, CheckConstraint, text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()

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

    # UPI Details
    upi_id = Column(String(100))
    upi_holder_name = Column(String(100))
    bank_name = Column(String(100))
    is_upi_bound = Column(Boolean, default=False)

    # Status
    is_active = Column(Boolean, default=True)
    is_blocked = Column(Boolean, default=False)

    # Timestamps
    created_at = Column(DateTime, default='CURRENT_TIMESTAMP')
    updated_at = Column(DateTime, default='CURRENT_TIMESTAMP')
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

class Admin(Base):
    __tablename__ = 'admins'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=True, nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(20), default='admin', nullable=False)
    permissions = Column(JSON)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))
    last_login_at = Column(DateTime, nullable=True)

    # Relationships
    transactions_reviewed = relationship("Transaction", back_populates="admin")
    activity_logs = relationship("ActivityLog", back_populates="admin")
    settings_updated = relationship("PlatformSetting", back_populates="updated_by")

    __table_args__ = (
        CheckConstraint("role IN ('super_admin', 'admin', 'support')"),
    )

class CryptoWallet(Base):
    __tablename__ = 'crypto_wallets'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    network_type = Column(String(20), nullable=False)
    wallet_address = Column(String(100), unique=True, nullable=False)
    currency = Column(String(10), default='USDT')
    is_active = Column(Boolean, default=True)
    assigned_to_user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    created_at = Column(DateTime, default='CURRENT_TIMESTAMP')
    updated_at = Column(DateTime, default='CURRENT_TIMESTAMP')

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
        CheckConstraint("type IN ('deposit', 'withdrawal', 'commission')"),
        CheckConstraint("status IN ('pending', 'processing', 'approved', 'rejected', 'completed', 'failed')"),
    )

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

class TeamMember(Base):
    __tablename__ = 'team_members'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    parent_user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    child_user_id = Column(BigInteger, ForeignKey('users.id'), nullable=False)
    level = Column(Integer, default=1)

    created_at = Column(DateTime, default='CURRENT_TIMESTAMP')

    # Relationships
    parent = relationship("User", foreign_keys=[parent_user_id], back_populates="team_members")
    child = relationship("User", foreign_keys=[child_user_id], back_populates="child_team_members")

    __table_args__ = (
        UniqueConstraint('parent_user_id', 'child_user_id'),
    )

class PlatformSetting(Base):
    __tablename__ = 'platform_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    setting_key = Column(String(50), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    data_type = Column(String(20), default='string')
    description = Column(Text)

    updated_by_admin_id = Column(BigInteger, ForeignKey('admins.id'))
    updated_at = Column(DateTime, default='CURRENT_TIMESTAMP')

    # Relationships
    updated_by = relationship("Admin", back_populates="settings_updated")

    __table_args__ = (
        CheckConstraint("data_type IN ('string', 'number', 'boolean', 'json')"),
    )

class ActivityLog(Base):
    __tablename__ = 'activity_logs'

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    user_id = Column(BigInteger, ForeignKey('users.id'), nullable=True)
    admin_id = Column(BigInteger, ForeignKey('admins.id'), nullable=True)

    action_type = Column(String(50), nullable=False)
    entity_type = Column(String(50))
    entity_id = Column(BigInteger)

    description = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(Text)
    log_metadata = Column(JSON)

    created_at = Column(DateTime, default='CURRENT_TIMESTAMP')

    # Relationships
    user = relationship("User", back_populates="activity_logs")
    admin = relationship("Admin", back_populates="activity_logs")

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

    created_at = Column(DateTime, default='CURRENT_TIMESTAMP')

    # Relationships
    user = relationship("User", back_populates="notifications")
    transaction = relationship("Transaction", back_populates="notifications")

    __table_args__ = (
        CheckConstraint("type IN ('info', 'success', 'warning', 'transaction')"),
    )

# Indexes
Index('idx_users_phone', User.phone_number)
Index('idx_users_referral_code', User.referral_code)
Index('idx_users_referred_by', User.referred_by_user_id)
Index('idx_admins_username', Admin.username)
Index('idx_admins_email', Admin.email)
Index('idx_crypto_wallets_network', CryptoWallet.network_type)
Index('idx_crypto_wallets_address', CryptoWallet.wallet_address)
Index('idx_transactions_user', Transaction.user_id)
Index('idx_transactions_status', Transaction.status)
Index('idx_transactions_type', Transaction.type)
Index('idx_transactions_created_at', Transaction.created_at)
Index('idx_commissions_referrer', Commission.referrer_user_id)
Index('idx_commissions_transaction', Commission.transaction_id)
Index('idx_team_members_parent', TeamMember.parent_user_id)
Index('idx_team_members_child', TeamMember.child_user_id)
Index('idx_platform_settings_key', PlatformSetting.setting_key)
Index('idx_activity_logs_user', ActivityLog.user_id)
Index('idx_activity_logs_admin', ActivityLog.admin_id)
Index('idx_activity_logs_action', ActivityLog.action_type)
Index('idx_activity_logs_created_at', ActivityLog.created_at)
Index('idx_notifications_user', Notification.user_id)
Index('idx_notifications_read', Notification.is_read)