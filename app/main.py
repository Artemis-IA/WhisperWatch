# app/main.py
from fastapi import FastAPI
from app.api import video_api
from app.schemas.user import UserCreate, UserDB, UserUpdate
from app.db.database import init_db
from app.core.user_manager import fastapi_users, auth_backend
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
def on_startup():
    init_db()

# Include auth routes
app.include_router(fastapi_users.get_auth_router(auth_backend), prefix="/auth/jwt", tags=["auth"])
app.include_router(fastapi_users.get_register_router(UserDB, UserCreate), prefix="/auth", tags=["auth"])
app.include_router(fastapi_users.get_users_router(UserDB, UserUpdate), prefix="/users", tags=["users"])

# Include video API routes
app.include_router(video_api.router, prefix="/api", tags=["videos"])
