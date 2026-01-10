import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.db.database import init_db
from app.routers import auth, user, transactions, dashboard, notifications, storage, app_config

@asynccontextmanager
async def lifespan(_app: FastAPI):
    # Initialize database tables
    init_db()
    yield

app = FastAPI(title=settings.app_name, lifespan=lifespan)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth, tags=["Authentication"])
app.include_router(user, tags=["User"])
app.include_router(transactions, tags=["Transactions"])
app.include_router(dashboard, tags=["Dashboard"])
app.include_router(notifications, tags=["Notifications"])
app.include_router(app_config, tags=["App Config"])

@app.get("/")
def root():
    return {"message": "Dollar Pay API is running"}

@app.get("/storage/upload")
def storage_upload():
    return {"url": "https://public.bnbstatic.com/image/cms/article/body/202206/f9f2f9ebb1a4caf7e477a7613788ccb8.png"}

@app.get("/health")
def health_check():
    return {"status": "healthy"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=settings.debug)
