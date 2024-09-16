import torch
from loguru import logger

class MLModelManager:
    def __init__(self, model_name: str, device: str = None):
        self.model_name = model_name
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
        # Implement model loading based on model_name
        raise NotImplementedError("This should be implemented in subclasses.")

    def to_device(self, data):
        """Helper function to move data to the correct device."""
        return data.to(self.device)
