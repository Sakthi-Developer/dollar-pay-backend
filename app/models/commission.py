from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from decimal import Decimal
from enum import Enum


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
    created_at: datetime

    class Config:
        from_attributes = True
