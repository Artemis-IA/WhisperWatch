# app/services/relevance_service.py
import numpy as np
from services.embedding_service import EmbeddingService
from services.transcription_service import TranscriptionService
import json
from typing import List

class RelevanceDetectionService:
    def __init__(self, keywords_file="keywords.json"):
        self.embedding_service = EmbeddingService()
        self.transcription_service = TranscriptionService()
        self.load_keywords(keywords_file)

    def load_keywords(self, keywords_file):
        with open(keywords_file, 'r') as f:
            self.keywords = json.load(f)

    def is_relevant(self, content: str) -> bool:
        """Vérifie si le contenu est pertinent basé sur les mots-clés et les embeddings."""
        # Vérifier que content est bien une chaîne de caractères
        if not isinstance(content, str):
            raise ValueError(f"Le contenu doit être une chaîne de caractères, obtenu: {type(content)}")

        # Découpage sémantique du contenu
        chunks = self.embedding_service.semantic_chunking(content)

        # Vérification basée sur les mots-clés
        for chunk in chunks:
            for keyword in self.keywords:
                if keyword.lower() in chunk.lower():
                    return True

        # Vérification basée sur les embeddings
        content_embedding = self.embedding_service.encode(content)
        for keyword in self.keywords:
            keyword_embedding = self.embedding_service.encode(keyword)
            similarity = np.dot(content_embedding, keyword_embedding.T)
            if similarity > 0.8:  # Ajuster le seuil de pertinence si nécessaire
                return True

        return False

    def check_relevance_from_audio(self, audio_input):
        """Transcrit et vérifie la pertinence du contenu audio."""
        transcription = self.transcription_service.transcribe_audio(audio_input)
        # Vérifier que la transcription est une chaîne de caractères
        if not isinstance(transcription, str):
            raise ValueError(f"La transcription doit être une chaîne de caractères, obtenu: {type(transcription)}")
        return self.is_relevant(transcription)
