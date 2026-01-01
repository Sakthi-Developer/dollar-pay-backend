from pydantic import BaseModel, field_validator, EmailStr
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
import re


class UserRegister(BaseModel):
    phone_number: str
    password: str
    referral_code: Optional[str] = None

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r"^\+?[1-9]\d{9,14}$", v):
            raise ValueError("Invalid phone number format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserLogin(BaseModel):
    phone_number: str
    password: str


class UserProfile(BaseModel):
    id: int
    name: Optional[str] = None
    email: Optional[str] = None
    phone_number: str
    upi_id: Optional[str] = None
    upi_holder_name: Optional[str] = None
    bank_name: Optional[str] = None
    wallet_balance: float = 0.0
    total_deposited: Optional[float] = 0.0
    total_withdrawn: Optional[float] = 0.0
    total_commission_earned: Optional[float] = 0.0
    referral_code: str
    is_upi_bound: Optional[bool] = False
    is_active: Optional[bool] = True
    created_at: datetime

    class Config:
        from_attributes = True


class UserResponse(BaseModel):
    id: int
    phone_number: str
    referral_code: str
    message: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserProfile


class UpdateProfile(BaseModel):
    name: Optional[str] = None
    email: Optional[EmailStr] = None


class BindUPI(BaseModel):
    upi_id: str
    upi_holder_name: str
    bank_name: str

    @field_validator("upi_id")
    @classmethod
    def validate_upi(cls, v):
        if not re.match(r"^[\w.-]+@[\w]+$", v):
            raise ValueError("Invalid UPI ID format")
        return v
