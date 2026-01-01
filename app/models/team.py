from sqlalchemy import Column, Integer, DateTime, BigInteger, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.models.base import Base

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
