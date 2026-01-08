from pydantic import BaseModel, field_serializer
from typing import Optional
from datetime import datetime
from enum import Enum

from app.core.utils import to_ist


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

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> datetime:
        return to_ist(value)

    class Config:
        from_attributes = True
