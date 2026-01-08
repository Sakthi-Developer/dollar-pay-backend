from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum

from app.core.utils import to_ist


class CommissionStatus(str, Enum):
    PENDING = "pending"
    CREDITED = "credited"
    CANCELLED = "cancelled"


class CommissionResponse(BaseModel):
    id: int
    referrer_user_id: int
    referred_user_id: int
    transaction_id: int
    commission_percent: Decimal
    base_amount: Decimal
    commission_amount: Decimal
    status: CommissionStatus
    credited_at: Optional[datetime] = None
    created_at: Optional[datetime] = None

    @field_serializer("credited_at", "created_at")
    def serialize_datetimes(self, value: Optional[datetime]) -> Optional[datetime]:
        return to_ist(value)

    class Config:
        from_attributes = True
