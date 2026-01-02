from sqlalchemy import Column, String, DateTime, Text, BigInteger, ForeignKey, JSON, text
from sqlalchemy.orm import relationship
from app.models.base import Base

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

    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'))

    # Relationships
    user = relationship("User", back_populates="activity_logs")
    admin = relationship("Admin", back_populates="activity_logs")
