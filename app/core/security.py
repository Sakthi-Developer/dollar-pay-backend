from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.core.config import settings
from app.db.database import get_db_context
from app.db.models import User, Admin

security = HTTPBearer()


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    payload = decode_token(credentials.credentials)
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    with get_db_context() as db:
        user = db.query(User).filter_by(id=int(user_id), is_active=True, is_blocked=False).first()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return {
        "id": user.id,
        "phone_number": user.phone_number,
        "referral_code": user.referral_code,
        "name": user.name,
        "email": user.email,
        "wallet_balance": float(user.wallet_balance),
        "total_deposited": float(user.total_deposited),
        "total_withdrawn": float(user.total_withdrawn),
        "total_commission_earned": float(user.total_commission_earned),
        "upi_id": user.upi_id,
        "upi_holder_name": user.upi_holder_name,
        "bank_name": user.bank_name,
        "is_upi_bound": user.is_upi_bound,
        "is_active": user.is_active,
        "created_at": user.created_at
    }


def get_current_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    payload = decode_token(credentials.credentials)
    admin_id = payload.get("sub")
    if admin_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )

    with get_db_context() as db:
        admin = db.query(Admin).filter_by(id=int(admin_id), is_active=True).first()
        if admin is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Admin not found or inactive",
            )

    return {
        "id": admin.id,
        "username": admin.username,
        "email": admin.email,
        "role": admin.role,
        "permissions": admin.permissions,
        "is_active": admin.is_active,
        "created_at": admin.created_at
    }


def get_current_super_admin(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current super admin user."""
    admin_data = get_current_admin(credentials)
    if admin_data["role"] != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Super admin access required",
        )
    return admin_data
