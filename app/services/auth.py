import bcrypt
import psycopg
import secrets
import string
from datetime import datetime, timezone
from fastapi import HTTPException
from app.db import get_db
from app.models import UserRegister, UserLogin, UserProfile, UserResponse, TokenResponse
from app.core.security import create_access_token


class AuthService:
    @staticmethod
    def generate_referral_code(length: int = 8) -> str:
        """Generate a unique referral code."""
        chars = string.ascii_uppercase + string.digits
        return "".join(secrets.choice(chars) for _ in range(length))

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

    @staticmethod
    def verify_password(password: str, hashed: str) -> bool:
        return bcrypt.checkpw(password.encode(), hashed.encode())

    @staticmethod
    def get_unique_referral_code() -> str:
        """Generate a unique referral code that doesn't exist in the database."""
        with get_db() as conn:
            while True:
                code = AuthService.generate_referral_code()
                existing = conn.execute(
                    "SELECT id FROM users WHERE referral_code = %s", (code,)
                ).fetchone()
                if not existing:
                    return code

    @staticmethod
    def register_user(user: UserRegister) -> UserResponse:
        password_hash = AuthService.hash_password(user.password)
        referral_code = AuthService.get_unique_referral_code()

        referred_by_user_id = None
        if user.referral_code:
            with get_db() as conn:
                referrer = conn.execute(
                    "SELECT id FROM users WHERE referral_code = %s",
                    (user.referral_code,)
                ).fetchone()
                if not referrer:
                    raise HTTPException(status_code=400, detail="Invalid referral code")
                referred_by_user_id = referrer["id"]

        with get_db() as conn:
            try:
                result = conn.execute(
                    """
                    INSERT INTO users (phone_number, password_hash, referral_code, referred_by_code, referred_by_user_id)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, phone_number, referral_code
                    """,
                    (user.phone_number, password_hash, referral_code, user.referral_code, referred_by_user_id)
                ).fetchone()
                conn.commit()

                new_user_id = result["id"]

                # Create team member relationship if referred
                if referred_by_user_id:
                    # Direct referral (level 1)
                    conn.execute(
                        "INSERT INTO team_members (parent_user_id, child_user_id, level) VALUES (%s, %s, %s)",
                        (referred_by_user_id, new_user_id, 1)
                    )

                    # Get parent's referrers for indirect relationships
                    parents = conn.execute(
                        """
                        SELECT parent_user_id, level FROM team_members
                        WHERE child_user_id = %s ORDER BY level
                        """,
                        (referred_by_user_id,)
                    ).fetchall()

                    for parent in parents:
                        new_level = parent["level"] + 1
                        conn.execute(
                            "INSERT INTO team_members (parent_user_id, child_user_id, level) VALUES (%s, %s, %s)",
                            (parent["parent_user_id"], new_user_id, new_level)
                        )

                    conn.commit()

                return UserResponse(
                    id=result["id"],
                    phone_number=result["phone_number"],
                    referral_code=result["referral_code"],
                    message="User registered successfully"
                )
            except psycopg.errors.UniqueViolation:
                conn.rollback()
                raise HTTPException(status_code=400, detail="Phone number already registered")

    @staticmethod
    def login_user(user: UserLogin) -> TokenResponse:
        with get_db() as conn:
            db_user = conn.execute(
                "SELECT * FROM users WHERE phone_number = %s",
                (user.phone_number,)
            ).fetchone()

            if not db_user:
                raise HTTPException(status_code=401, detail="Invalid phone number or password")

            if not AuthService.verify_password(user.password, db_user["password_hash"]):
                raise HTTPException(status_code=401, detail="Invalid phone number or password")

            if db_user["is_blocked"]:
                raise HTTPException(status_code=403, detail="Account is blocked")

            if not db_user["is_active"]:
                raise HTTPException(status_code=403, detail="Account is inactive")

            # Update last login
            conn.execute(
                "UPDATE users SET last_login_at = %s WHERE id = %s",
                (datetime.now(timezone.utc), db_user["id"])
            )
            conn.commit()

            # Create access token
            access_token = create_access_token(data={"sub": str(db_user["id"])})

            user_profile = UserProfile(
                id=db_user["id"],
                phone_number=db_user["phone_number"],
                referral_code=db_user["referral_code"],
                name=db_user["name"],
                email=db_user["email"],
                wallet_balance=db_user["wallet_balance"],
                total_deposited=db_user["total_deposited"],
                total_withdrawn=db_user["total_withdrawn"],
                total_commission_earned=db_user["total_commission_earned"],
                upi_id=db_user["upi_id"],
                upi_holder_name=db_user["upi_holder_name"],
                bank_name=db_user["bank_name"],
                is_upi_bound=db_user["is_upi_bound"],
                is_active=db_user["is_active"],
                created_at=db_user["created_at"]
            )

            return TokenResponse(
                access_token=access_token,
                user=user_profile
            )
