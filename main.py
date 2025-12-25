from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, field_validator
import psycopg
from psycopg.rows import dict_row
import bcrypt
import re
import os

app = FastAPI(title="Dollar Pay API")

DATABASE_URL = "postgresql://neondb_owner:npg_PJmsvHaC40Fk@ep-damp-lake-a4gktx6k-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"


def get_db_connection():
    return psycopg.connect(DATABASE_URL, row_factory=dict_row)


def init_db():
    with get_db_connection() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                phone_number VARCHAR(15) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()


class UserRegister(BaseModel):
    phone_number: str
    password: str

    @field_validator("phone_number")
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r"^\+?[1-9]\d{9,14}$", v):
            raise ValueError("Invalid phone number format")
        return v

    @field_validator("password")
    @classmethod
    def validate_password(cls, v):
        if len(v) < 6:
            raise ValueError("Password must be at least 6 characters")
        return v


class UserResponse(BaseModel):
    id: int
    phone_number: str
    message: str


@app.on_event("startup")
def on_startup():
    init_db()


@app.post("/register", response_model=UserResponse)
def register_user(user: UserRegister):
    password_hash = bcrypt.hashpw(user.password.encode(), bcrypt.gensalt()).decode()

    with get_db_connection() as conn:
        try:
            result = conn.execute(
                "INSERT INTO users (phone_number, password_hash) VALUES (%s, %s) RETURNING id, phone_number",
                (user.phone_number, password_hash)
            ).fetchone()
            conn.commit()

            return UserResponse(
                id=result["id"],
                phone_number=result["phone_number"],
                message="User registered successfully"
            )
        except psycopg.errors.UniqueViolation:
            conn.rollback()
            raise HTTPException(status_code=400, detail="Phone number already registered")


@app.get("/")
def root():
    return {"message": "Dollar Pay API"}


if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
