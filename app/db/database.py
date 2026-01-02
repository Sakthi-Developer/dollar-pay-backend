from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
from app.models import Base
from app.models.user import User
from app.core.config import settings
from contextlib import contextmanager

# Create engine with connection pooling and SSL parameters for Neon
engine = create_engine(
    settings.database_url,
    echo=False,
    poolclass=QueuePool,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=3600,  # Recycle connections every hour
    pool_pre_ping=True,  # Enable connection health checks
    connect_args={
        "sslmode": "require",
        "connect_timeout": 10,
        "keepalives": 1,
        "keepalives_idle": 30,
        "keepalives_interval": 10,
        "keepalives_count": 5,
    }
)
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
