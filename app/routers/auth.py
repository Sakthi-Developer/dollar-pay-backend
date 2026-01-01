from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from app.models import UserRegister, UserLogin, UserResponse, TokenResponse, UserProfile, AdminRegister, AdminResponse, AdminLogin
from app.db.database import get_db_context
from app.db.models import User, TeamMember, Admin
from app.core.security import get_current_user, create_access_token, get_current_super_admin
import bcrypt
import secrets
import string
from datetime import datetime, timezone

router = APIRouter(prefix="/auth", tags=["Authentication"])


def generate_referral_code(length: int = 8) -> str:
    """Generate a unique referral code."""
    chars = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())


def get_unique_referral_code(db) -> str:
    """Generate a unique referral code that doesn't exist in the database."""
    while True:
        code = generate_referral_code()
        existing = db.query(User).filter_by(referral_code=code).first()
        if not existing:
            return code


@router.post("/register", response_model=UserResponse)
def register(user: UserRegister):
    """Register a new user with phone number, password, and optional referral code."""
    with get_db_context() as db:
        password_hash = hash_password(user.password)
        referral_code = get_unique_referral_code(db)

        referred_by_user_id = None
        if user.referral_code:
            referrer = db.query(User).filter_by(referral_code=user.referral_code).first()
            if not referrer:
                raise HTTPException(status_code=400, detail="Invalid referral code")
            referred_by_user_id = referrer.id

        try:
            new_user = User(
                phone_number=user.phone_number,
                password_hash=password_hash,
                referral_code=referral_code,
                referred_by_code=user.referral_code,
                referred_by_user_id=referred_by_user_id
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)

            new_user_id = new_user.id

            # Create team member relationship if referred
            if referred_by_user_id:
                # Direct referral (level 1)
                team_member = TeamMember(
                    parent_user_id=referred_by_user_id,
                    child_user_id=new_user_id,
                    level=1
                )
                db.add(team_member)

                # Get parent's referrers for indirect relationships
                parents = db.query(TeamMember).filter_by(child_user_id=referred_by_user_id).order_by(TeamMember.level).all()

                for parent in parents:
                    new_level = parent.level + 1
                    indirect_team_member = TeamMember(
                        parent_user_id=parent.parent_user_id,
                        child_user_id=new_user_id,
                        level=new_level
                    )
                    db.add(indirect_team_member)

                db.commit()

            return UserResponse(
                id=new_user.id,
                phone_number=new_user.phone_number,
                referral_code=new_user.referral_code,
                message="User registered successfully"
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Phone number already registered")


@router.post("/login", response_model=TokenResponse)
def login(user: UserLogin):
    """Login with phone number and password. Returns JWT token."""
    with get_db_context() as db:
        db_user = db.query(User).filter_by(phone_number=user.phone_number).first()

        if not db_user:
            raise HTTPException(status_code=401, detail="Invalid phone number or password")

        if not verify_password(user.password, db_user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid phone number or password")

        if db_user.is_blocked:
            raise HTTPException(status_code=403, detail="Account is blocked")

        if not db_user.is_active:
            raise HTTPException(status_code=403, detail="Account is inactive")

        # Update last login
        db_user.last_login_at = datetime.now(timezone.utc)
        db.commit()

        # Create access token
        access_token = create_access_token(data={"sub": str(db_user.id)})

        user_profile = UserProfile(
            id=db_user.id,
            phone_number=db_user.phone_number,
            referral_code=db_user.referral_code,
            name=db_user.name,
            email=db_user.email,
            wallet_balance=float(db_user.wallet_balance),
            total_deposited=float(db_user.total_deposited),
            total_withdrawn=float(db_user.total_withdrawn),
            total_commission_earned=float(db_user.total_commission_earned),
            upi_id=db_user.upi_id,
            upi_holder_name=db_user.upi_holder_name,
            bank_name=db_user.bank_name,
            is_upi_bound=db_user.is_upi_bound,
            is_active=db_user.is_active,
            created_at=db_user.created_at
        )

        return TokenResponse(
            access_token=access_token,
            user=user_profile
        )


@router.post("/admin/register", response_model=AdminResponse)
def admin_register(admin: AdminRegister, current_super_admin: dict = Depends(get_current_super_admin)):
    """Register a new admin user. Only super admins can create new admins."""
    # TODO: Add authentication check for super admin
    # For now, allowing registration without auth for initial setup
    
    with get_db_context() as db:
        password_hash = hash_password(admin.password)
        
        try:
            new_admin = Admin(
                username=admin.username,
                email=admin.email,
                password_hash=password_hash,
                role=admin.role
            )
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)

            return AdminResponse(
                id=new_admin.id,
                username=new_admin.username,
                email=new_admin.email,
                role=new_admin.role,
                is_active=new_admin.is_active,
                created_at=new_admin.created_at,
                message="Admin registered successfully"
            )
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Username or email already exists")


@router.post("/admin/login", response_model=TokenResponse)
def admin_login(admin_credentials: AdminLogin):
    """Admin login with username and password. Returns JWT token."""
    with get_db_context() as db:
        db_admin = db.query(Admin).filter_by(username=admin_credentials.username).first()

        if not db_admin:
            raise HTTPException(status_code=401, detail="Invalid username or password")

        if not verify_password(admin_credentials.password, db_admin.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")

        if not db_admin.is_active:
            raise HTTPException(status_code=403, detail="Account is inactive")

        # Update last login
        db_admin.last_login_at = datetime.now(timezone.utc)
        db.commit()

        # Create access token
        access_token = create_access_token(data={"sub": str(db_admin.id)})

        # Return token with admin info (using user field for compatibility)
        admin_profile = UserProfile(
            id=db_admin.id,
            phone_number=db_admin.username,
            referral_code="",
            name=db_admin.username,
            email=db_admin.email,
            wallet_balance=0.0,
            total_deposited=0.0,
            total_withdrawn=0.0,
            total_commission_earned=0.0,
            upi_id="",
            upi_holder_name="",
            bank_name="",
            is_upi_bound=False,
            is_active=db_admin.is_active,
            created_at=db_admin.created_at
        )

        return TokenResponse(
            access_token=access_token,
            user=admin_profile
        )


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
