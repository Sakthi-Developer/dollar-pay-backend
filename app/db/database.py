from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.db.models import Base, User
from app.core.config import settings
from contextlib import contextmanager

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """Get database session for FastAPI dependency injection."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_db_context():
    """Get database session as a context manager for direct usage."""
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
        with get_db_context() as db:
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
        with get_db_context() as db:
            return db.query(User).filter_by(id=user_id).first()

    @staticmethod
    def save_user(user):
        with get_db_context() as db:
            db.add(user)
            db.commit()
            db.refresh(user)
            return user


db = Database()
