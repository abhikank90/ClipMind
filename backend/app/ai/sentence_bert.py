import logging
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Union

logger = logging.getLogger(__name__)


class SentenceBERTEmbedder:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize Sentence-BERT model
        
        Popular models:
        - all-MiniLM-L6-v2: Fast, 384 dimensions
        - all-mpnet-base-v2: High quality, 768 dimensions
        """
        logger.info(f"Loading Sentence-BERT model: {model_name}")
        self.model = SentenceTransformer(model_name)
        self.embedding_dim = self.model.get_sentence_embedding_dimension()
    
    def encode(self, text: Union[str, List[str]]) -> np.ndarray:
        """Generate embeddings for text"""
        try:
            if isinstance(text, str):
                text = [text]
            
            embeddings = self.model.encode(
                text,
                convert_to_numpy=True,
                show_progress_bar=False
            )
            
            return embeddings
            
        except Exception as e:
            logger.error(f"Text encoding failed: {e}")
            # Return zero vector on failure
            if isinstance(text, str):
                return np.zeros(self.embedding_dim)
            else:
                return np.zeros((len(text), self.embedding_dim))
    
    def compute_similarity(self, text1: str, text2: str) -> float:
        """Compute semantic similarity between two texts"""
        embeddings = self.encode([text1, text2])
        
        # Cosine similarity
        similarity = np.dot(embeddings[0], embeddings[1]) / (
            np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
        )
        
        return float(similarity)
    
    def find_most_similar(self, query: str, candidates: List[str], top_k: int = 5) -> List[tuple]:
        """Find most similar texts to query"""
        query_embedding = self.encode(query)
        candidate_embeddings = self.encode(candidates)
        
        # Compute similarities
        similarities = np.dot(candidate_embeddings, query_embedding) / (
            np.linalg.norm(candidate_embeddings, axis=1) * np.linalg.norm(query_embedding)
        )
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = [
            (candidates[idx], float(similarities[idx]))
            for idx in top_indices
        ]
        
        return results
