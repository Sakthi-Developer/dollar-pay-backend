import bcrypt
import secrets
import string
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from app.models.user import User
from app.models.team import TeamMember
from app.models.admin import Admin
from app.schemas.user import UserRegister, UserLogin, AdminRegister, AdminLogin
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

    @classmethod
    def get_unique_referral_code(cls, db: Session) -> str:
        """Generate a unique referral code that doesn't exist in the database."""
        while True:
            code = cls.generate_referral_code()
            existing = db.query(User).filter_by(referral_code=code).first()
            if not existing:
                return code

    @classmethod
    def register_user(cls, db: Session, user_data: UserRegister) -> User:
        password_hash = cls.hash_password(user_data.password)
        referral_code = cls.get_unique_referral_code(db)

        referred_by_user_id = None
        if user_data.referral_code:
            referrer = db.query(User).filter_by(referral_code=user_data.referral_code).first()
            if not referrer:
                raise HTTPException(status_code=400, detail="Invalid referral code")
            referred_by_user_id = referrer.id

        try:
            new_user = User(
                phone_number=user_data.phone_number,
                password_hash=password_hash,
                referral_code=referral_code,
                referred_by_code=user_data.referral_code,
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

            return new_user
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Phone number already registered")

    @classmethod
    def login_user(cls, db: Session, login_data: UserLogin) -> dict:
        user = db.query(User).filter_by(phone_number=login_data.phone_number).first()
        if not user or not cls.verify_password(login_data.password, user.password_hash):
            raise HTTPException(status_code=401, detail="Invalid phone number or password")
        
        if not user.is_active:
            raise HTTPException(status_code=400, detail="Account is inactive")
        
        if user.is_blocked:
            raise HTTPException(status_code=400, detail="Account is blocked")

        access_token = create_access_token(data={"sub": str(user.id), "role": "user"})
        return {"access_token": access_token, "token_type": "bearer"}

    @classmethod
    def register_admin(cls, db: Session, admin_data: AdminRegister) -> Admin:
        password_hash = cls.hash_password(admin_data.password)
        
        try:
            new_admin = Admin(
                username=admin_data.username,
                email=admin_data.email,
                password_hash=password_hash,
                role=admin_data.role,
                permissions=admin_data.permissions
            )
            db.add(new_admin)
            db.commit()
            db.refresh(new_admin)
            return new_admin
        except IntegrityError:
            db.rollback()
            raise HTTPException(status_code=400, detail="Username or email already registered")

    @classmethod
    def login_admin(cls, db: Session, login_data: AdminLogin) -> dict:
        admin = db.query(Admin).filter_by(username=login_data.username).first()
        if not admin or not cls.verify_password(login_data.password, admin.password_hash):
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        if not admin.is_active:
            raise HTTPException(status_code=400, detail="Account is inactive")

        access_token = create_access_token(data={"sub": str(admin.id), "role": admin.role})
        return {"access_token": access_token, "token_type": "bearer"}

auth_service = AuthService()
