from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.schemas.user import UserRegister, UserLogin, UserResponse, TokenResponse, AdminRegister, AdminResponse, AdminLogin, AdminTokenResponse
from app.services.auth_service import auth_service
from app.core.security import get_current_user, get_current_super_admin

router = APIRouter()

@router.post("/auth/register", response_model=UserResponse)
def register(user: UserRegister, db: Session = Depends(get_db)):
    """Register a new user with phone number, password, and optional referral code."""
    new_user = auth_service.register_user(db, user)
    return UserResponse(
        id=new_user.id,
        phone_number=new_user.phone_number,
        referral_code=new_user.referral_code,
        message="User registered successfully"
    )

@router.post("/auth/login", response_model=TokenResponse)
def login(user: UserLogin, db: Session = Depends(get_db)):
    """Login user and return JWT token."""
    return auth_service.login_user(db, user)

@router.post("/auth/admin/register", response_model=AdminResponse)
def register_admin(
    admin: AdminRegister, 
    current_admin: dict = Depends(get_current_super_admin),
    db: Session = Depends(get_db)
):
    """Register a new admin (Super Admin only)."""
    new_admin = auth_service.register_admin(db, admin)
    return AdminResponse(
        id=new_admin.id,
        username=new_admin.username,
        email=new_admin.email,
        role=new_admin.role,
        message="Admin registered successfully"
    )

@router.post("/auth/admin/login", response_model=AdminTokenResponse)
def login_admin(admin: AdminLogin, db: Session = Depends(get_db)):
    """Login admin and return JWT token."""
    return auth_service.login_admin(db, admin)
