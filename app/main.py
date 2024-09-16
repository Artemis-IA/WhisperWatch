from fastapi import FastAPI
from api import auth, video_api, keywords_api, relevance_api
from db.database import init_db
from prometheus_fastapi_instrumentator import Instrumentator
from apscheduler.schedulers.background import BackgroundScheduler
from services.orchestrator import ServiceOrchestrator
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI application
app = FastAPI()

# Initialize services orchestrator
orchestrator = ServiceOrchestrator()

# Initialize Prometheus for monitoring
Instrumentator().instrument(app).expose(app)

# Initialize Background Scheduler
scheduler = BackgroundScheduler()

@app.on_event("startup")
def on_startup():
    # Initialize the database
    init_db()

    # Start orchestrating the services
    orchestrator.schedule_tasks()

    # Schedule automated tasks using APScheduler
    scheduler.start()

@app.on_event("shutdown")
def on_shutdown():
    # Clean shutdown when FastAPI stops
    print("Shutting down APIntelligence...")
    orchestrator.shutdown_services()
    scheduler.shutdown()

# Include authentication routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include video API routes
app.include_router(video_api.router, prefix="/api", tags=["videos"])

# Include keywords API routes
app.include_router(keywords_api.router, prefix="/keywords", tags=["keywords"])

# Include relevance API routes
app.include_router(relevance_api.router, prefix="/relevance", tags=["relevance"])
