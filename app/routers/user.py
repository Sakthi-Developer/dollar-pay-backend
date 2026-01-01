from fastapi import APIRouter, Depends, HTTPException, Query
from app.models import UpdateProfile, BindUPI, UserProfile
from app.services import UserService
from app.core.security import get_current_user

router = APIRouter(prefix="/user", tags=["User"])


@router.put("/update", response_model=UserProfile)
def update_user_details(
    update_data: UpdateProfile, current_user: dict = Depends(get_current_user)
):
    """Update user details like name and email."""
    updated_user = UserService.update_user_details(current_user["id"], update_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.post("/bind-upi", response_model=UserProfile)
def bind_upi(
    upi_data: BindUPI, current_user: dict = Depends(get_current_user)
):
    """Bind UPI ID to the user's account."""
    updated_user = UserService.bind_upi(current_user["id"], upi_data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.get("/upi", response_model=dict)
def get_upi_id(current_user: dict = Depends(get_current_user)):
    """Get the UPI ID bound to the user's account."""
    upi_id = current_user.get("upi_id")
    if not upi_id:
        raise HTTPException(status_code=404, detail="UPI ID not found")
    return {"upi_id": upi_id}


@router.get("/all", response_model=list[UserProfile])
def get_all_users(
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user)
):
    """Get all users with pagination."""
    users = UserService.get_all_users(limit=limit, offset=offset)
    if not users:
        raise HTTPException(status_code=404, detail="No users found")
    return users
