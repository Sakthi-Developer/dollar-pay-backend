from pydantic import BaseModel, field_serializer
from datetime import datetime
from decimal import Decimal
from typing import Optional

from app.core.utils import to_ist


class TeamMember(BaseModel):
    id: int
    user_id: int
    phone_number: str
    name: Optional[str] = None
    level: int
    total_deposited: Decimal = Decimal("0.00")
    joined_at: datetime

    @field_serializer("joined_at")
    def serialize_joined_at(self, value: datetime) -> datetime:
        return to_ist(value)

    class Config:
        from_attributes = True


class TeamStats(BaseModel):
    total_members: int
    direct_members: int
    indirect_members: int
    total_commission_earned: Decimal
    team_total_deposited: Decimal
