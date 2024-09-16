# app/services/relevance_service.py

import numpy as np
from services.embedding_service import EmbeddingService
from services.transcription_service import TranscriptionService
import json

class RelevanceDetectionService:
    def __init__(self, keywords_file="keywords.json"):
        self.embedding_service = EmbeddingService()
        self.transcription_service = TranscriptionService()
        self.load_keywords(keywords_file)

    def load_keywords(self, keywords_file):
        with open(keywords_file, 'r') as f:
            self.keywords = json.load(f)

    def is_relevant(self, content: str) -> bool:
        """Check if content is relevant based on keywords and embeddings."""
        # Chunk the content first
        chunks = self.embedding_service.chunk_text(content)

        # Keyword-based relevance check
        for chunk in chunks:
            for keyword in self.keywords:
                if keyword.lower() in chunk.lower():
                    return True

        # Embedding-based relevance check
        content_embedding = self.embedding_service.get_embedding(content)
        for keyword in self.keywords:
            keyword_embedding = self.embedding_service.get_embedding(keyword)
            similarity = np.dot(content_embedding, keyword_embedding.T)
            if similarity > 0.8:  # Adjust the threshold for relevance
                return True

        return False

    def check_relevance_from_video(self, video_path: str):
        """Extract audio, transcribe, and check relevance of video content."""
        transcription = self.transcription_service.transcribe_video(video_path)
        return self.is_relevant(transcription)

    def check_relevance_from_audio(self, audio_bytes: bytes):
        """Transcribe and check relevance of audio content."""
        transcription = self.transcription_service.transcribe_audio(audio_bytes)
        return self.is_relevant(transcription)
