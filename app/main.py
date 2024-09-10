# app/main.py
from fastapi import FastAPI
from app.api import auth, video_api, keywords_api
from app.schemas.user import UserCreate, UserDB, UserUpdate
from app.db.database import init_db
from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI()
Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
def on_startup():
    init_db()

# Include auth routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include video API routes
app.include_router(video_api.router, prefix="/api", tags=["videos"])
app.include_router(keywords_api.router, prefix="/keywords", tags=["keywords"])  # Add route for keywords

