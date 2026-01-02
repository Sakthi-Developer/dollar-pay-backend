from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserProfile, TeamMemberSchema, CommissionSchema, BindUPI
from app.services.user_service import user_service
from app.core.security import get_current_user

router = APIRouter()

@router.get("/profile", response_model=UserProfile)
def get_profile(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current user profile with wallet balance and team stats."""
    return user_service.get_user_profile(db, current_user['id'])

@router.get("/team", response_model=List[TeamMemberSchema])
def get_team(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get list of team members referred by the current user."""
    return user_service.get_team_members(db, current_user['id'])

@router.get("/commissions", response_model=List[CommissionSchema])
def get_commissions(
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get history of commissions earned."""
    return user_service.get_commissions(db, current_user['id'])

@router.put("/bind-upi", response_model=UserProfile)
def bind_upi(
    upi_data: BindUPI,
    current_user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Bind UPI details to user account."""
    return user_service.bind_upi(db, current_user['id'], upi_data)
