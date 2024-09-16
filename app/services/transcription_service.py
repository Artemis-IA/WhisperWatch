# app/services/transcription_service.py
from transformers import pipeline
from core.config import settings
import torch


class TranscriptionService:
    def __init__(self, model_name="openai/whisper-small"):
        # Utilisez la configuration pour sélectionner le dispositif
        device = 0 if settings.USE_GPU else -1
        self.transcriber = pipeline(
            "automatic-speech-recognition",
            model=model_name,
            device=-1
        )

    def transcribe_audio(self, audio_file_path):
        result = self.transcriber(audio_file_path)
        return result['text']
