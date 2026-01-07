from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserProfile, TeamMemberSchema, CommissionSchema, BindUPI, BindBankAccount, PaginatedUserResponse
from app.services.user_service import user_service
from app.core.security import get_current_user, get_current_admin
from app.models.user import User

router = APIRouter()

@router.get("/user/profile", response_model=UserProfile)
def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile with wallet balance and team stats."""
    return user_service.get_user_profile(db, current_user['id'])

@router.get("/user/team", response_model=List[TeamMemberSchema])
def get_team(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of team members referred by the current user."""
    return user_service.get_team_members(db, current_user['id'])

@router.get("/user/commissions", response_model=List[CommissionSchema])
def get_commissions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get history of commissions earned."""
    return user_service.get_commissions(db, current_user['id'])

@router.put("/user/bind-upi", response_model=UserProfile)
def bind_upi(
    upi_data: BindUPI,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bind UPI details to user account."""
    return user_service.bind_upi(db, current_user['id'], upi_data)

@router.put("/user/bind-bank-account", response_model=UserProfile)
def bind_bank_account(
    bank_data: BindBankAccount,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bind bank account details (IMPS) to user account."""
    return user_service.bind_bank_account(db, current_user['id'], bank_data)

# Admin endpoints

@router.get("/admin/users/search", response_model=PaginatedUserResponse)
def search_users(
    mobile_number: str,
    page: int = 1,
    limit: int = 20,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Search users by mobile number."""
    query = db.query(User).filter(User.phone_number.ilike(f"%{mobile_number}%"))

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    # Create UserProfile objects with team size and commission
    user_profiles = []
    for user in users:
        user_profiles.append(user_service.get_user_profile(db, user.id))

    return PaginatedUserResponse(
        users=user_profiles,
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit
    )

@router.get("/admin/users", response_model=PaginatedUserResponse)
def get_all_users(
    page: int = 1,
    limit: int = 20,
    search: str = None,
    current_admin: dict = Depends(get_current_admin),
    db: Session = Depends(get_db)
):
    """Get all users with pagination for admin."""
    query = db.query(User)
    if search:
        query = query.filter(
            (User.name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%")) |
            (User.phone_number.ilike(f"%{search}%"))
        )

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset((page - 1) * limit).limit(limit).all()

    # Create UserProfile objects with team size and commission
    user_profiles = []
    for user in users:
        user_profiles.append(user_service.get_user_profile(db, user.id))

    return PaginatedUserResponse(
        users=user_profiles,
        total=total,
        page=page,
        limit=limit,
        total_pages=(total + limit - 1) // limit
    )
