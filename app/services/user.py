from app.models import UpdateProfile, BindUPI, UserProfile

from app.db import get_db as db

class UserService:
    @staticmethod
    def update_user_details(user_id: int, update_data: UpdateProfile) -> UserProfile:
        """Update user details like name and email."""
        user = db.get_user_by_id(user_id)
        if not user:
            return None
        user.name = update_data.name
        user.email = update_data.email
        db.save_user(user)
        return user

    @staticmethod
    def bind_upi(user_id: int, upi_data: BindUPI) -> UserProfile:
        """Bind UPI ID to the user's account."""
        user = db.get_user_by_id(user_id)
        if not user:
            return None
        user.upi_id = upi_data.upi_id
        db.save_user(user)
        return user

    @staticmethod
    def get_all_users(limit: int, offset: int) -> list[UserProfile]:
        """Get all users with pagination."""
        users = db.get_users(limit=limit, offset=offset)
        return users