# app/core/models_garden.py
import torch
from loguru import logger
from sentence_transformers import SentenceTransformer
from transformers import pipeline

class MLModelManager:
    def __init__(self, model_name: str, model_type: str, device: str = None):
        self.model_name = model_name
        self.model_type = model_type
        self.device = device or self._get_device()
        self.model = self._load_model()

    def _get_device(self) -> str:
        if torch.cuda.is_available():
            logger.info("GPU is available. Using CUDA.")
            return "cuda"
        elif getattr(torch, "has_mps", False):
            logger.info("Apple Silicon available. Using MPS.")
            return "mps"
        else:
            logger.info("Using CPU.")
            return "cpu"

    def _load_model(self):
        if self.model_type == 'embedding':
            # Charger le modèle SentenceTransformer
            model = SentenceTransformer(self.model_name, device=self.device)
        elif self.model_type == 'transcription':
            # Charger le pipeline de transcription
            device_index = 0 if self.device == 'cuda' else -1
            model = pipeline(
                "automatic-speech-recognition",
                model=self.model_name,
                device=device_index
            )
        else:
            raise ValueError(f"Unsupported model type: {self.model_type}")
        return model

    def to_device(self, data):
        """Fonction pour déplacer les données vers le bon dispositif."""
        return data.to(self.device)
