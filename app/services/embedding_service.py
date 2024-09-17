# app/services/embedding_service.py
from typing import List
import numpy as np
from functools import lru_cache
from core.models_garden import MLModelManager
import psycopg2
from pgvector.psycopg2 import register_vector

class EmbeddingService:
    def __init__(
        self,
        model_name: str = "sentence-transformers/all-MiniLM-L6-v2",  # Modèle par défaut léger
        batch_size: int = 32,
        device: str = None,
        normalize_embeddings: bool = True,
    ):
        self.model_name = model_name
        self.batch_size = batch_size
        self.device = device
        self.normalize_embeddings = normalize_embeddings
        self.model_manager = MLModelManager(
            model_name=self.model_name,
            model_type='embedding',
            device=self.device
        )
        self.model = self.model_manager.model
        self.dimension: int = self.model.get_sentence_embedding_dimension()
        self.pg_conn = None  # Connexion à PostgreSQL

    @lru_cache(maxsize=128)
    def encode(self, text: str) -> np.ndarray:
        """Génère les embeddings pour un seul texte."""
        return self.model.encode(
            text,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize_embeddings,
        )

    def encode_batch(self, texts: List[str]) -> np.ndarray:
        """Génère les embeddings pour une liste de textes."""
        return self.model.encode(
            texts,
            batch_size=self.batch_size,
            normalize_embeddings=self.normalize_embeddings,
        )

    def semantic_chunking(self, text: str, chunk_size: int = 512) -> List[str]:
        """Effectue le découpage sémantique des textes longs pour l'embedding."""
        words = text.split()
        chunks = [' '.join(words[i:i + chunk_size]) for i in range(0, len(words), chunk_size)]
        return chunks

    # Méthodes pour la gestion de PostgreSQL avec pgvector
    def connect_to_pgvector(self, database_url: str):
        """Connecte à PostgreSQL avec l'extension pgvector activée."""
        try:
            self.pg_conn = psycopg2.connect(database_url)
            register_vector(self.pg_conn)
            print("Connecté à PostgreSQL avec pgvector.")
        except Exception as e:
            raise Exception(f"Erreur de connexion à PostgreSQL: {str(e)}")

    def store_embedding(self, text: str, embedding: np.ndarray, table_name: str = "embeddings"):
        """Stocke les embeddings dans la base de données PostgreSQL en utilisant pgvector."""
        if not self.pg_conn:
            raise Exception("Non connecté à PostgreSQL. Appelez d'abord connect_to_pgvector().")
        
        with self.pg_conn.cursor() as cur:
            cur.execute(f"""
                INSERT INTO {table_name} (text, embedding)
                VALUES (%s, %s::vector)
            """, (text, embedding.tolist()))
        self.pg_conn.commit()

    def retrieve_similar_texts(self, query_embedding: np.ndarray, table_name: str = "embeddings", top_n: int = 5) -> List[dict]:
        """Récupère les textes les plus similaires basés sur la similarité cosinus en utilisant pgvector."""
        if not self.pg_conn:
            raise Exception("Non connecté à PostgreSQL. Appelez d'abord connect_to_pgvector().")
        
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
        """Ferme la connexion PostgreSQL."""
        if self.pg_conn:
            self.pg_conn.close()
            print("Connexion PostgreSQL fermée.")

    def generate_similarity(self, source_sentence: str, target_sentences: List[str]) -> List[float]:
        """Calcule la similarité entre une phrase source et une liste de phrases cibles en utilisant les embeddings."""
        source_embedding = self.encode(source_sentence)
        target_embeddings = self.encode_batch(target_sentences)
        
        similarities = np.dot(target_embeddings, source_embedding.T)
        return similarities.tolist()