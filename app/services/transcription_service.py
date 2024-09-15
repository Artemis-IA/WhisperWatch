# app/services/transcription_service.py
from transformers import pipeline

class TranscriptionService:
    def __init__(self, model_name="openai/whisper-small"):
        self.transcriber = pipeline("automatic-speech-recognition",
                                    model=model_name,
                                    device=0)

    def transcribe_audio(self, audio_file_path):
        result = self.transcriber(audio_file_path)
        return result['text']
