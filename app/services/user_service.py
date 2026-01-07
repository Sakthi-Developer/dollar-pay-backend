from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.team import TeamMember
from app.models.commission import Commission
from app.models.transaction import Transaction
from app.schemas.user import UserProfile, TeamMemberSchema, CommissionSchema, BindUPI, BindBankAccount

class UserService:
    def get_user_profile(self, db: Session, user_id: int) -> UserProfile:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate total team size (users where this user is the parent)
        team_size = db.query(TeamMember).filter(TeamMember.parent_user_id == user_id).count()
        
        # Calculate total commission (commissions where this user is the referrer)
        total_commission = 0
        commissions = db.query(Commission).filter(Commission.referrer_user_id == user_id).all()
        for comm in commissions:
            total_commission += float(comm.commission_amount)

        return UserProfile(
            id=user.id,
            name=user.name,
            email=user.email,
            phone_number=user.phone_number,
            upi_id=user.upi_id,
            upi_holder_name=user.upi_holder_name,
            bank_name=user.bank_name,
            is_upi_bound=user.is_upi_bound,
            account_number=user.account_number,
            ifsc_code=user.ifsc_code,
            account_holder_name=user.account_holder_name,
            is_bank_bound=user.is_bank_bound,
            wallet_balance=float(user.wallet_balance),
            total_deposited=float(user.total_deposited),
            total_withdrawn=float(user.total_withdrawn),
            total_commission_earned=float(user.total_commission_earned),
            total_usd_sent=float(user.total_usd_sent or 0),
            referral_code=user.referral_code,
            team_size=team_size,
            total_commission=total_commission,
            is_active=user.is_active,
            created_at=user.created_at
        )

    def get_team_members(self, db: Session, user_id: int):
        # Get team members where the current user is the parent
        members = db.query(TeamMember).filter(TeamMember.parent_user_id == user_id).all()
        result = []
        for member in members:
            # Get the child user details
            user_details = db.query(User).filter(User.id == member.child_user_id).first()
            if user_details:
                result.append(TeamMemberSchema(
                    user_id=user_details.id,
                    phone_number=user_details.phone_number,
                    joined_at=member.created_at,
                    level=member.level
                ))
        return result

    def get_commissions(self, db: Session, user_id: int):
        # Get commissions where this user is the referrer (earned the commission)
        commissions = db.query(Commission).filter(Commission.referrer_user_id == user_id).order_by(Commission.created_at.desc()).all()
        return [
            CommissionSchema(
                id=c.id,
                amount=float(c.commission_amount),
                from_user_id=c.referred_user_id,
                level=1,  # Level info not stored in commission, default to 1
                created_at=c.created_at
            ) for c in commissions
        ]

    def bind_upi(self, db: Session, user_id: int, upi_data: BindUPI) -> UserProfile:
        """Bind UPI details to user account and clear IMPS data."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update UPI details
        user.upi_id = upi_data.upi_id
        user.upi_holder_name = upi_data.upi_holder_name
        user.bank_name = upi_data.bank_name
        user.is_upi_bound = True

        # Clear IMPS/bank account data completely
        user.account_number = None
        user.ifsc_code = None
        user.account_holder_name = None
        user.is_bank_bound = False

        db.commit()
        db.refresh(user)

        # Return updated profile
        return self.get_user_profile(db, user_id)

    def bind_bank_account(self, db: Session, user_id: int, bank_data: BindBankAccount) -> UserProfile:
        """Bind bank account details (IMPS) to user account and clear UPI data."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Update bank account details
        user.account_number = bank_data.account_number
        user.ifsc_code = bank_data.ifsc_code
        user.account_holder_name = bank_data.account_holder_name
        user.bank_name = bank_data.bank_name
        user.is_bank_bound = True

        # Clear UPI data completely
        user.upi_id = None
        user.upi_holder_name = None
        user.is_upi_bound = False

        db.commit()
        db.refresh(user)

        # Return updated profile
        return self.get_user_profile(db, user_id)

user_service = UserService()
