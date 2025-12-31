from fastapi import APIRouter, Depends
from app.models import UserRegister, UserLogin, UserResponse, TokenResponse, UserProfile
from app.services import AuthService
from app.core.security import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse)
def register(user: UserRegister):
    """Register a new user with phone number, password, and optional referral code."""
    return AuthService.register_user(user)


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    """Login with phone number and password. Returns JWT token."""
    return AuthService.login_user(user)


@router.get("/me", response_model=UserProfile)
def get_me(current_user: dict = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return UserProfile(
        id=current_user["id"],
        phone_number=current_user["phone_number"],
        referral_code=current_user["referral_code"],
        name=current_user["name"],
        email=current_user["email"],
        wallet_balance=current_user["wallet_balance"],
        total_deposited=current_user["total_deposited"],
        total_withdrawn=current_user["total_withdrawn"],
        total_commission_earned=current_user["total_commission_earned"],
        upi_id=current_user["upi_id"],
        upi_holder_name=current_user["upi_holder_name"],
        bank_name=current_user["bank_name"],
        is_upi_bound=current_user["is_upi_bound"],
        is_active=current_user["is_active"],
        created_at=current_user["created_at"]
    )
