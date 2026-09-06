"""
Lightweight CPU Vector Store & Semantic Similarity Engine for Project Jarvis.
Runs embeddings strictly on CPU (0 MB VRAM) using all-MiniLM-L6-v2 with fallback.
"""

import math
from typing import List, Dict, Any, Optional, Tuple
import numpy as np

class VectorStore:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", device: str = "cpu"):
        self.model_name = model_name
        self.device = device
        self._model = None
        self._is_st_available = None

    def _get_model(self):
        """Lazy loader for sentence-transformers on CPU."""
        if self._is_st_available is False:
            return None

        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                print(f"[VectorStore] Loading embedding model '{self.model_name}' on {self.device}...")
                self._model = SentenceTransformer(self.model_name, device=self.device)
                self._is_st_available = True
                print("[VectorStore] ✅ Embedding model ready on CPU.")
            except Exception as e:
                print(f"[VectorStore] SentenceTransformer not installed or failed ({e}). Using semantic keyword fallback.")
                self._is_st_available = False
                self._model = None
        return self._model

    def encode(self, text: str) -> np.ndarray:
        """Compute 384-dim normalized embedding on CPU."""
        model = self._get_model()
        if model is not None:
            emb = model.encode(text, convert_to_numpy=True, normalize_embeddings=True)
            return emb.astype(np.float32)
        
        # Fallback pseudo-embedding based on character n-grams and hashing
        dim = 128
        vec = np.zeros(dim, dtype=np.float32)
        words = text.lower().split()
        for w in words:
            h = hash(w) % dim
            vec[h] += 1.0
        norm = np.linalg.norm(vec)
        if norm > 0:
            vec = vec / norm
        return vec

    def serialize_embedding(self, emb: np.ndarray) -> bytes:
        """Convert numpy array to bytes for SQLite storage."""
        return emb.astype(np.float32).tobytes()

    def deserialize_embedding(self, blob: bytes) -> np.ndarray:
        """Convert SQLite blob back to float32 numpy array."""
        return np.frombuffer(blob, dtype=np.float32)

    def search_top_k(
        self,
        query: str,
        memories: List[Dict[str, Any]],
        top_k: int = 4,
        threshold: float = 0.25
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Rank candidate memories by semantic similarity to the query string.
        Returns list of (memory_dict, similarity_score).
        """
        if not memories:
            return []

        query_vec = self.encode(query)
        scored_items = []

        for mem in memories:
            emb_blob = mem.get("embedding")
            if emb_blob:
                try:
                    mem_vec = self.deserialize_embedding(emb_blob)
                except Exception:
                    mem_vec = self.encode(f"{mem.get('topic', '')}: {mem.get('content', '')}")
            else:
                mem_vec = self.encode(f"{mem.get('topic', '')}: {mem.get('content', '')}")

            # Compute Cosine Similarity (vectors are unit normalized)
            sim = float(np.dot(query_vec, mem_vec))
            
            # Additional keyword match boost
            topic_lower = mem.get("topic", "").lower()
            if topic_lower and topic_lower in query.lower():
                sim += 0.35

            if sim >= threshold:
                scored_items.append((mem, sim))

        # Sort descending by score
        scored_items.sort(key=lambda x: x[1], reverse=True)
        return scored_items[:top_k]
