# Dollar Pay Backend - AI Coding Guidelines

## Architecture Overview
This is a FastAPI-based backend for a crypto payment platform ("Dollar Pay") handling USDT deposits/withdrawals with referral commissions and team hierarchies.

**Key Components:**
- `app/routers/`: API endpoints with business logic (auth.py for authentication, user.py for user operations)
- `app/models/`: Pydantic models for request/response validation (e.g., UserRegister in user.py)
- `app/db/`: Database layer with SQLAlchemy ORM (models.py defines tables, database.py for session management)
- `app/core/`: Configuration (config.py with Pydantic settings) and security (JWT tokens)
- `alembic/`: Database migrations

**Data Flow:**
- User registration/login via `/auth` endpoints with direct DB operations
- All authenticated routes use `Depends(get_current_user)` from `app/core/security.py`
- Transactions involve crypto wallets, admin reviews, and commission calculations

**Structural Decisions:**
- Simplified: No service layer - logic in routers
- Single DB session per request using context manager in `database.py`
- Referral system with hierarchical teams (team_members table) and commission tracking

## Development Workflow
- **Environment**: Use virtual environment (`.venv/`) activated via `& .venv\Scripts\Activate.ps1`
- **Run Locally**: `python main.py` (uses uvicorn with reload if debug=True in settings)
- **Database**: PostgreSQL with connection string in `.env` (DATABASE_URL)
- **Migrations**: Use Alembic (`alembic revision --autogenerate -m "message"`, `alembic upgrade head`)
- **Dependencies**: Install from `requirements.txt` (includes SQLAlchemy for ORM, psycopg2 for Postgres, bcrypt for passwords)

## Code Patterns
- **Models**: Use Pydantic BaseModel with validators (e.g., phone number regex in UserRegister); SQLAlchemy models in `app/db/models.py`
- **Database**: SQLAlchemy ORM with sessionmaker, use `get_db()` context manager for sessions
- **Authentication**: JWT tokens created in `security.py`, verified via dependency injection
- **Passwords**: Hash with bcrypt in routers
- **Referral Codes**: Auto-generated unique 8-char codes using secrets module
- **Settings**: Cached via `@lru_cache` in config.py, loaded from `.env`

## Key Files to Reference
- `main.py`: App entry point with CORS and router inclusion
- `app/db/models.py`: SQLAlchemy models for all tables
- `app/db/database.py`: Session management and DB utilities
- `app/routers/auth.py`: User registration/login logic with referral handling
- `app/core/config.py`: Environment-based configuration
- `alembic/versions/`: Migration files
- `requirements.txt`: Exact dependency versions

## Integration Points
- **Database**: PostgreSQL with SQLAlchemy ORM (psycopg2 driver)
- **External**: None currently (crypto wallet addresses stored in DB)
- **Deployment**: Docker (Dockerfile, docker-compose.yml) and Render (render.yaml)

Avoid adding tests or async patterns unless explicitly requested - stick to synchronous FastAPI with blocking DB calls.</content>
<parameter name="filePath">c:\Users\sakth\OneDrive\Desktop\dollar-pay-backend\.github\copilot-instructions.md