# app/services/embedding_service.py
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List
from functools import lru_cache
import torch
from pgvector.psycopg2 import register_vector
import psycopg2

# Helper function to get device (CUDA, MPS, CPU)
def get_torch_device() -> str:
    return (
        "mps"
        if getattr(torch, "has_mps", False)
        else "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

class EmbeddingService:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",  # Lightweight default model
        batch_size: int = 32,
        device: str = get_torch_device(),
        normalize_embeddings: bool = True,
    ):
        self.model_name = model_name
        self.model = self._load_model(model_name)
        self.batch_size = batch_size
        self.device = device
        self.normalize_embeddings = normalize_embeddings
        self.dimension: int = self.model.get_sentence_embedding_dimension()
        self.pg_conn = None  # Connection to PostgreSQL

    def _load_model(self, model_name: str) -> SentenceTransformer:
        """Load a SentenceTransformer model with error handling."""
        try:
            return SentenceTransformer(model_name)
        except Exception as e:
            raise Exception(f"Error loading model {model_name}: {str(e)}")

    @lru_cache(maxsize=128)
    def encode(self, text: str) -> np.ndarray:
        """Generate embeddings for a single text input."""
        return self.model.encode(
            text,
            batch_size=self.batch_size,
            device=self.device,
            normalize_embeddings=self.normalize_embeddings,
        )

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Generate embeddings for a batch of text inputs."""
        return self.model.encode(
            texts,
            batch_size=self.batch_size,
            device=self.device,
            normalize_embeddings=self.normalize_embeddings,
        )

    def semantic_chunking(self, text: str, chunk_size: int = 512) -> List[str]:
        """Perform semantic chunking of long texts for embedding."""
        words = text.split()
        chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        return chunks

    def connect_to_pgvector(self, database_url: str):
        """Connect to PostgreSQL with pgvector extension enabled."""
        try:
            self.pg_conn = psycopg2.connect(database_url)
            register_vector(self.pg_conn)
            print("Connected to PostgreSQL with pgvector.")
        except Exception as e:
            raise Exception(f"Error connecting to PostgreSQL: {str(e)}")

    def store_embedding(self, text: str, embedding: np.ndarray, table_name: str = "embeddings"):
        """Store embeddings in the PostgreSQL database using pgvector."""
        if not self.pg_conn:
            raise Exception("Not connected to PostgreSQL. Call `connect_to_pgvector()` first.")
        
        with self.pg_conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {table_name} (text, embedding)
                VALUES (%s, %s::vector)
            """, (text, embedding.tolist()))
        self.pg_conn.commit()

    def retrieve_similar_texts(self, query_embedding: np.ndarray, table_name: str = "embeddings", top_n: int = 5) -> List[dict]:
        """Retrieve top-N most similar texts based on cosine similarity using pgvector."""
        if not self.pg_conn:
            raise Exception("Not connected to PostgreSQL. Call `connect_to_pgvector()` first.")
        
        with self.pg_conn.cursor() as cur:
            cur.execute(f"""
                SELECT text, embedding
                FROM {table_name}
                ORDER BY embedding <-> %s::vector
                LIMIT %s
            """, (query_embedding.tolist(), top_n))
            results = cur.fetchall()
        
        return [{"text": row[0], "similarity": row[1]} for row in results]

    def close_pg_connection(self):
        """Close the PostgreSQL connection."""
        if self.pg_conn:
            self.pg_conn.close()
            print("PostgreSQL connection closed.")
    
    def generate_similarity(self, source_sentence: str, target_sentences: List[str]) -> List[float]:
        """Compute similarity between a source sentence and a list of target sentences using embeddings."""
        source_embedding = self.encode(source_sentence)
        target_embeddings = self.encode_batch(target_sentences)
        
        similarities = np.dot(target_embeddings, source_embedding.T)
        return similarities.tolist()
