# app/main.py
from fastapi import FastAPI
from api import auth, video_api, keywords_api, relevance_api
from db.database import init_db
from prometheus_fastapi_instrumentator import Instrumentator
from services.download_service import DownloadService
from services.video_hunt import VideoHunterService
from services.etdqn import ETDQN
from services.kafka_manager import KafkaManager
from services.relevance_service import RelevanceDetectionService
from services.youtube_service import YouTubeService
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Define a central class for orchestrating the different services
class ServiceOrchestrator:
    def __init__(self):
        self.download_service = DownloadService()
        self.youtube_service = YouTubeService()
        self.relevance_service = RelevanceDetectionService()
        self.etdqn_agent = ETDQN(input_dim=2, output_dim=2)
        self.video_hunter = VideoHunterService(
            youtube_service=self.youtube_service,
            keyword_manager=self.relevance_service,  # Assume relevance_service manages keywords
            relevance_service=self.relevance_service,
            etdqn=self.etdqn_agent
        )
        self.kafka_manager = KafkaManager(topic_name=os.getenv('KAFKA_TOPIC_NEW_VIDEOS'))

    def start_video_hunt(self):
        relevant_videos = self.video_hunter.hunt_videos()
        for video in relevant_videos:
            print(f"Relevant video found: {video['title']}")
            # You can further enhance this to publish to Kafka or process these videos.

    def start_kafka_consumer(self):
        # Start consuming Kafka messages and downloading videos
        self.download_service.consume_and_download()

    def orchestrate_all(self):
        # This method is called at startup to orchestrate the processes
        self.start_kafka_consumer()
        self.start_video_hunt()

# Central Orchestrator instance
orchestrator = ServiceOrchestrator()

# FastAPI Application
app = FastAPI()

# Prometheus for monitoring
Instrumentator().instrument(app).expose(app)

@app.on_event("startup")
def on_startup():
    # Initialize the database
    init_db()
    # Start orchestrating the services
    orchestrator.orchestrate_all()

# Include auth routes
app.include_router(auth.router, prefix="/auth", tags=["auth"])

# Include video API routes
app.include_router(video_api.router, prefix="/api", tags=["videos"])

# Include keywords API routes
app.include_router(keywords_api.router, prefix="/keywords", tags=["keywords"])

# Include relevance API routes
app.include_router(relevance_api.router, prefix="/relevance", tags=["relevance"])
