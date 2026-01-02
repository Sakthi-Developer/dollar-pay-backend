from sqlalchemy import Column, Integer, String, DateTime, Text, BigInteger, ForeignKey, CheckConstraint, text
from sqlalchemy.orm import relationship
from app.models.base import Base

class PlatformSetting(Base):
    __tablename__ = 'platform_settings'

    id = Column(Integer, primary_key=True, autoincrement=True)
    setting_key = Column(String(50), unique=True, nullable=False)
    setting_value = Column(Text, nullable=False)
    data_type = Column(String(20), default='string')
    description = Column(Text)

    updated_by_admin_id = Column(BigInteger, ForeignKey('admins.id'))
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    updated_by = relationship("Admin", back_populates="settings_updated")

    __table_args__ = (
        CheckConstraint("data_type IN ('string', 'number', 'boolean', 'json')"),
    )
