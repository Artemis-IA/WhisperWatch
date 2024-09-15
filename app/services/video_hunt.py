# app/services/video_hunt.py
import numpy as np


class VideoHunterService:
    def __init__(self, youtube_service, keyword_manager, relevance_service, etdqn):
        self.youtube_service = youtube_service
        self.keyword_manager = keyword_manager
        self.relevance_service = relevance_service
        self.etdqn = etdqn

    def hunt_videos(self):
        videos = self.youtube_service.search_videos(query="tech", max_results=50)
        relevant_videos = []

        for video in videos:
            metadata = {
                "title": video["snippet"]["title"],
                "description": video["snippet"]["description"],
            }
            
            # Step 1: NLP relevance check
            if self.relevance_service.is_relevant(metadata, self.keyword_manager.keywords):
                # Step 2: ETDQN decision-making
                state = np.array([metadata['title'], metadata['description']])  # Simplified
                action = self.etdqn.choose_action(state)

                if action == 1:  # Action: Download and process
                    relevant_videos.append(video)

        return relevant_videos
