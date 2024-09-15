# app/services/relevance_service.py
from transformers import pipeline
import json
import os

class RelevanceDetectionService:
    def __init__(self, model_name="bert-base-uncased", keywords_file = "keywords.json"
):
        self.model = pipeline("text-classification",
                              model=model_name,
                              device=0)
        self.load_keywords(keywords_file)

    def load_keywords(self, keywords_file):
        if os.path.exists(keywords_file):
            with open(keywords_file, 'r') as f:
                self.keywords = json.load(f)
        else:
            raise FileNotFoundError(f"{keywords_file} does not exist")


    def is_relevant(self, video_metadata):
        video_text = f"{video_metadata['title']} {video_metadata['description']}"
        # Basic keyword matching
        for keyword in self.keywords:
            if keyword in video_text.lower():
                return True
        # Model-based relevance detection
        prediction = self.model(video_text)
        return prediction[0]['label'] == 'RELEVANT'
