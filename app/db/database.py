from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.db.models import Base
from app.core.config import settings

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session as a context manager."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialize database tables."""
    Base.metadata.create_all(bind=engine)


class Database:
    @staticmethod
    def get_users(limit, offset):
        with get_db() as db:
            users = db.query(User).order_by(User.id).offset(offset).limit(limit).all()
            return [
                {
                    'id': user.id,
                    'name': user.name,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'upi_id': user.upi_id,
                    'wallet_balance': float(user.wallet_balance),
                    'referral_code': user.referral_code,
                    'created_at': user.created_at
                }
                for user in users
            ]

    @staticmethod
    def get_user_by_id(user_id: int):
        with get_db() as db:
            return db.query(User).filter_by(id=user_id).first()

    @staticmethod
    def save_user(user):
        with get_db() as db:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user


db = Database()
