from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from typing import List
from app.models import UpdateProfile, BindUPI, UserProfile
from app.db.database import get_db_context
from app.db.models import User
from app.core.security import get_current_user

class PaginatedUsers(BaseModel):
    total: int
    limit: int
    offset: int
    items: List[UserProfile]

router = APIRouter(prefix="/user", tags=["User"])


@router.put("/update", response_model=UserProfile)
def update_user_details(
    update_data: UpdateProfile, current_user: dict = Depends(get_current_user)
):
    """Update user details like name and email."""
    with get_db_context() as db:
        user = db.query(User).filter_by(id=current_user["id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.name = update_data.name
        user.email = update_data.email
        db.commit()
        db.refresh(user)
        return UserProfile(
            id=user.id,
            phone_number=user.phone_number,
            referral_code=user.referral_code,
            name=user.name,
            email=user.email,
            wallet_balance=float(user.wallet_balance),
            upi_id=user.upi_id,
            upi_holder_name=user.upi_holder_name,
            bank_name=user.bank_name,
            is_upi_bound=user.is_upi_bound,
            is_active=user.is_active,
            created_at=user.created_at
        )


@router.post("/bind-upi", response_model=UserProfile)
def bind_upi(
    upi_data: BindUPI, current_user: dict = Depends(get_current_user)
):
    """Bind UPI ID to the user's account."""
    with get_db_context() as db:
        user = db.query(User).filter_by(id=current_user["id"]).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        user.upi_id = upi_data.upi_id
        user.upi_holder_name = upi_data.upi_holder_name
        user.bank_name = upi_data.bank_name
        user.is_upi_bound = True
        db.commit()
        db.refresh(user)
        return UserProfile(
            id=user.id,
            phone_number=user.phone_number,
            referral_code=user.referral_code,
            name=user.name,
            email=user.email,
            wallet_balance=float(user.wallet_balance),
            upi_id=user.upi_id,
            upi_holder_name=user.upi_holder_name,
            bank_name=user.bank_name,
            is_upi_bound=user.is_upi_bound,
            is_active=user.is_active,
            created_at=user.created_at
        )


@router.get("/upi", response_model=dict)
def get_upi_id(current_user: dict = Depends(get_current_user)):
    """Get the UPI ID bound to the user's account."""
    upi_id = current_user.get("upi_id")
    if not upi_id:
        raise HTTPException(status_code=404, detail="UPI ID not found")
    return {"upi_id": upi_id}


@router.get("/all", response_model=PaginatedUsers)
def get_all_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get all users with pagination."""
    with get_db_context() as db:
        total_users = db.query(User).count()
        users_db = (
            db.query(User)
            .order_by(User.id)
            .offset(offset)
            .limit(limit)
            .all()
        )

        items = [
            UserProfile(
                id=user.id,
                phone_number=user.phone_number,
                referral_code=user.referral_code,
                name=user.name,
                email=user.email,
                wallet_balance=float(user.wallet_balance or 0),
                upi_id=user.upi_id,
                created_at=user.created_at,
            )
            for user in users_db
        ]

        return PaginatedUsers(
            total=total_users,
            limit=limit,
            offset=offset,
            items=items,
        )
