from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.team import TeamMember
from app.models.commission import Commission
from app.models.transaction import Transaction
from app.schemas.user import UserProfile, TeamMemberSchema, CommissionSchema

class UserService:
    def get_user_profile(self, db: Session, user_id: int) -> UserProfile:
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Calculate total team size
        team_size = db.query(TeamMember).filter(TeamMember.referrer_id == user_id).count()
        
        # Calculate total commission
        total_commission = 0
        commissions = db.query(Commission).filter(Commission.to_user_id == user_id).all()
        for comm in commissions:
            total_commission += comm.amount

        return UserProfile(
            id=user.id,
            phone_number=user.phone_number,
            referral_code=user.referral_code,
            wallet_balance=user.wallet_balance,
            team_size=team_size,
            total_commission=total_commission,
            is_active=user.is_active
        )

    def get_team_members(self, db: Session, user_id: int):
        members = db.query(TeamMember).filter(TeamMember.referrer_id == user_id).all()
        result = []
        for member in members:
            user_details = db.query(User).filter(User.id == member.user_id).first()
            if user_details:
                result.append(TeamMemberSchema(
                    user_id=user_details.id,
                    phone_number=user_details.phone_number,
                    joined_at=member.joined_at,
                    level=member.level
                ))
        return result

    def get_commissions(self, db: Session, user_id: int):
        commissions = db.query(Commission).filter(Commission.to_user_id == user_id).order_by(Commission.created_at.desc()).all()
        return [
            CommissionSchema(
                id=c.id,
                amount=c.amount,
                from_user_id=c.from_user_id,
                level=c.level,
                created_at=c.created_at
            ) for c in commissions
        ]

user_service = UserService()
