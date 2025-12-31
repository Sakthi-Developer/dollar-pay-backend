from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum


class NotificationType(str, Enum):
    INFO = "info"
    SUCCESS = "success"
    WARNING = "warning"
    TRANSACTION = "transaction"


class NotificationResponse(BaseModel):
    id: int
    title: str
    message: str
    type: NotificationType
    is_read: bool
    related_transaction_id: Optional[int] = None
    created_at: datetime

    class Config:
        from_attributes = True
