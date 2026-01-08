from pydantic import BaseModel, field_validator, field_serializer
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

from app.core.utils import to_ist


class TransactionType(str, Enum):
    CRYPTO_DEPOSIT = "crypto_deposit"
    UPI_PAYOUT = "upi_payout"
    WITHDRAWAL = "withdrawal"
    COMMISSION = "commission"


class TransactionStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"
    FAILED = "failed"


class DepositCreate(BaseModel):
    crypto_network: str
    crypto_amount: Decimal
    crypto_tx_hash: str
    user_notes: Optional[str] = None

    @field_validator("crypto_network")
    @classmethod
    def validate_network(cls, v):
        allowed = ["TRC20", "ERC20", "BEP20"]
        if v.upper() not in allowed:
            raise ValueError(f"Network must be one of: {', '.join(allowed)}")
        return v.upper()

    @field_validator("crypto_amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("crypto_tx_hash")
    @classmethod
    def validate_tx_hash(cls, v):
        if not v or not v.strip():
            raise ValueError("Transaction hash is required and cannot be empty")
        return v.strip()


class UPIPayoutCreate(BaseModel):
    user_phone: str
    upi_amount: Decimal
    payment_reference: str
    crypto_amount: Decimal
    remaining_crypto: Decimal
    crypto_network: str
    user_notes: Optional[str] = None

    @field_validator("upi_amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("crypto_amount")
    @classmethod
    def validate_crypto_amount(cls, v):
        if v <= 0:
            raise ValueError("Crypto amount must be greater than 0")
        return v

    @field_validator("remaining_crypto")
    @classmethod
    def validate_remaining_crypto(cls, v):
        if v < 0:
            raise ValueError("Remaining crypto cannot be negative")
        return v

    @field_validator("crypto_network")
    @classmethod
    def validate_network(cls, v):
        allowed = ["TRC20", "ERC20", "BEP20"]
        if v.upper() not in allowed:
            raise ValueError(f"Network must be one of: {', '.join(allowed)}")
        return v.upper()

    @field_validator("payment_reference")
    @classmethod
    def validate_reference(cls, v):
        if not v or not v.strip():
            raise ValueError("Payment reference is required and cannot be empty")
        return v.strip()

class AdminUPIPayoutCreate(BaseModel):
    user_phone: str
    upi_amount: Decimal
    payment_reference: str
    crypto_amount: Decimal
    remaining_crypto: Decimal
    crypto_network: str
    user_notes: Optional[str] = None
    admin_notes: Optional[str] = None

    @field_validator("upi_amount")
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Amount must be greater than 0")
        return v

    @field_validator("crypto_amount")
    @classmethod
    def validate_crypto_amount(cls, v):
        if v <= 0:
            raise ValueError("Crypto amount must be greater than 0")
        return v

    @field_validator("remaining_crypto")
    @classmethod
    def validate_remaining_crypto(cls, v):
        if v < 0:
            raise ValueError("Remaining crypto cannot be negative")
        return v

    @field_validator("crypto_network")
    @classmethod
    def validate_network(cls, v):
        allowed = ["TRC20", "ERC20", "BEP20"]
        if v.upper() not in allowed:
            raise ValueError(f"Network must be one of: {', '.join(allowed)}")
        return v.upper()

    @field_validator("payment_reference")
    @classmethod
    def validate_reference(cls, v):
        if not v or not v.strip():
            raise ValueError("Payment reference is required and cannot be empty")
        return v.strip()

class TransactionUserInfo(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: str
    referral_code: str

    class Config:
        from_attributes = True


class TransactionResponse(BaseModel):
    id: int
    transaction_uid: str
    type: TransactionType
    status: TransactionStatus
    user: TransactionUserInfo
    crypto_network: Optional[str] = None
    crypto_amount: Optional[Decimal] = None
    remaining_crypto: Optional[Decimal] = None
    gross_inr_amount: Optional[Decimal] = None
    net_inr_amount: Optional[Decimal] = None
    platform_fee_amount: Optional[Decimal] = None
    bonus_amount: Optional[Decimal] = None
    payment_reference: Optional[str] = None
    created_at: Optional[datetime] = None

    @field_serializer("created_at")
    def serialize_created_at(self, value: Optional[datetime]) -> Optional[datetime]:
        return to_ist(value)

    class Config:
        from_attributes = True


class TransactionDetail(TransactionResponse):
    crypto_wallet_address: Optional[str] = None
    crypto_tx_hash: Optional[str] = None
    user_notes: Optional[str] = None
    exchange_rate: Optional[Decimal] = None
    user_upi_id: Optional[str] = None
    rejection_reason: Optional[str] = None
    admin_reviewed_at: Optional[datetime] = None
    payment_completed_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    @field_serializer("admin_reviewed_at", "payment_completed_at", "updated_at")
    def serialize_datetimes(self, value: Optional[datetime]) -> Optional[datetime]:
        return to_ist(value)


class AdminTransactionApproval(BaseModel):
    status: TransactionStatus
    admin_notes: Optional[str] = None
    rejection_reason: Optional[str] = None
    payment_reference: Optional[str] = None  # UTR for UPI payout
    transaction_fee: Optional[Decimal] = None  # Bank transaction fee
    platform_fee: Optional[Decimal] = None  # Platform fee for payout


class PaginatedTransactionResponse(BaseModel):
    transactions: List[TransactionResponse]
    total: int
    page: int
    limit: int
    total_pages: int
