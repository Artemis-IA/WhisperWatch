# app/services/transcription_service.py
from core.models_garden import MLModelManager

class TranscriptionService:
    def __init__(self, model_name="openai/whisper-small", device: str = None):
        self.model_name = model_name
        self.device = device
        self.model_manager = MLModelManager(
            model_name=self.model_name,
            model_type='transcription',
            device=self.device
        )
        self.transcriber = self.model_manager.model

    def transcribe_audio(self, audio_input):
        """Transcrit un fichier audio ou des données audio."""
        result = self.transcriber(audio_input)
        # Retourner le texte de la transcription
        return result['text']

