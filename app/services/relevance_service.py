# app/services/relevance_service.py
from transformers import pipeline
from sentence_transformers import SentenceTransformer
from core.config import settings
import numpy as np
import json
import os

class RelevanceDetectionService:
    def __init__(self, model_name="bert-base-uncased", keywords_file="keywords.json"):
        # Utiliser la configuration pour sélectionner le dispositif
        device = 0 if settings.USE_GPU else -1
        self.model = pipeline(
            "text-classification",
            model=model_name,
            device=-1
        )
        self.load_keywords(keywords_file)
        # Utiliser Sentence-Transformers pour générer des embeddings plus puissants
        self.embedding_model = SentenceTransformer(
            'sentence-transformers/all-MiniLM-L6-v2',
            device="cpu"
        )

    def load_keywords(self, keywords_file):
        if os.path.exists(keywords_file):
            with open(keywords_file, 'r') as f:
                self.keywords = json.load(f)
        else:
            raise FileNotFoundError(f"{keywords_file} does not exist")

    def is_relevant(self, video_metadata):
        video_text = f"{video_metadata['title']} {video_metadata['description']}"
        for keyword in self.keywords:
            if keyword.lower() in video_text.lower():
                return True

        prediction = self.model(video_text)
        return prediction[0]['label'] == 'RELEVANT'

    def generate_related_keywords(self, keyword, top_n=5):
        """Generate related keywords dynamically using embeddings and external sources"""
        # Embed the input keyword
        keyword_vector = self.embedding_model.encode([keyword])
        
        # Dynamically generate similar words or phrases using embeddings
        similar_words = self._find_similar_words(keyword_vector, top_n)
        
        # Optionally, extend this with related terms found via NLP models
        return similar_words

    def _find_similar_words(self, keyword_vector, top_n=5):
        # Supposons que nous ayons un vocabulaire pré-encodé de mots-clés courants
        vocab = [
            "AI", "deep learning", "neural networks", "machine learning",
            "data science", "automation", "cloud computing", "blockchain"
        ]  
        vocab_vectors = self.embedding_model.encode(vocab)

        # Calculer la similarité entre le mot-clé d'entrée et chaque mot du vocabulaire
        similarities = np.dot(vocab_vectors, keyword_vector.T).flatten()

        # Obtenir les top_n mots similaires
        top_indices = np.argsort(similarities)[::-1][:top_n]
        return [vocab[i] for i in top_indices]
