from sqlalchemy import Column, String, Boolean, DateTime, BigInteger, JSON, CheckConstraint, text
from sqlalchemy.orm import relationship
from app.models.base import Base

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
