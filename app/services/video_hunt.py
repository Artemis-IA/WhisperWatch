# app/services/video_hunt.py
import numpy as np
from services.kafka_manager import KafkaManager

class VideoHunterService:
    def __init__(self, youtube_service, keyword_manager, relevance_service, etdqn, kafka_topic="video_events"):
        self.youtube_service = youtube_service
        self.keyword_manager = keyword_manager
        self.relevance_service = relevance_service
        self.etdqn = etdqn
        self.kafka_manager = KafkaManager(kafka_topic)

    def hunt_videos(self):
        # Get keywords from the manager
        keywords = self.keyword_manager.get_keywords()

        # Search videos
        for keyword in keywords:
            videos = self.youtube_service.search_videos(query=keyword, max_results=50)
            for video in videos:
                metadata = {
                    "title": video["snippet"]["title"],
                    "description": video["snippet"]["description"],
                }

                # Step 1: NLP relevance check
                if self.relevance_service.is_relevant(metadata):
                    # Step 2: ETDQN decision-making
                    state = np.array([metadata['title'], metadata['description']])
                    action = self.etdqn.choose_action(state)

                    if action == 1:  # Action: Download and process video
                        video_url = f"https://www.youtube.com/watch?v={video['id']['videoId']}"
                        self.kafka_manager.send_message("video_events", video_url)  # Send to Kafka for processing
