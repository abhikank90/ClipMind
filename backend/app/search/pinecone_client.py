import logging
from typing import List, Dict, Any, Optional
import numpy as np

logger = logging.getLogger(__name__)


class PineconeClient:
    def __init__(self, api_key: str, environment: str, index_name: str):
        """Initialize Pinecone client"""
        try:
            import pinecone
            
            pinecone.init(api_key=api_key, environment=environment)
            
            # Check if index exists, create if not
            if index_name not in pinecone.list_indexes():
                logger.info(f"Creating Pinecone index: {index_name}")
                pinecone.create_index(
                    name=index_name,
                    dimension=512,  # CLIP embedding dimension
                    metric="cosine"
                )
            
            self.index = pinecone.Index(index_name)
            logger.info(f"Connected to Pinecone index: {index_name}")
            
        except Exception as e:
            logger.error(f"Pinecone initialization failed: {e}")
            raise
    
    def upsert_vectors(
        self,
        vectors: List[Dict[str, Any]],
        namespace: str = ""
    ) -> bool:
        """
        Insert or update vectors in Pinecone
        
        vectors format: [
            {
                'id': 'clip_123',
                'values': [0.1, 0.2, ...],  # 512-dim embedding
                'metadata': {'video_id': 'video_1', 'start_time': 10.5}
            }
        ]
        """
        try:
            self.index.upsert(vectors=vectors, namespace=namespace)
            logger.info(f"Upserted {len(vectors)} vectors to Pinecone")
            return True
        except Exception as e:
            logger.error(f"Vector upsert failed: {e}")
            return False
    
    def query(
        self,
        query_vector: np.ndarray,
        top_k: int = 10,
        filter: Optional[Dict[str, Any]] = None,
        namespace: str = ""
    ) -> List[Dict[str, Any]]:
        """
        Query similar vectors from Pinecone
        
        Returns: [
            {
                'id': 'clip_123',
                'score': 0.95,
                'metadata': {...}
            }
        ]
        """
        try:
            results = self.index.query(
                vector=query_vector.tolist(),
                top_k=top_k,
                include_metadata=True,
                filter=filter,
                namespace=namespace
            )
            
            matches = results.get("matches", [])
            logger.info(f"Found {len(matches)} similar vectors")
            
            return [
                {
                    "id": match["id"],
                    "score": match["score"],
                    "metadata": match.get("metadata", {})
                }
                for match in matches
            ]
            
        except Exception as e:
            logger.error(f"Vector query failed: {e}")
            return []
    
    def delete_by_metadata(self, filter: Dict[str, Any], namespace: str = "") -> bool:
        """Delete vectors by metadata filter"""
        try:
            self.index.delete(filter=filter, namespace=namespace)
            logger.info(f"Deleted vectors with filter: {filter}")
            return True
        except Exception as e:
            logger.error(f"Vector deletion failed: {e}")
            return False
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get index statistics"""
        try:
            stats = self.index.describe_index_stats()
            return stats
        except Exception as e:
            logger.error(f"Failed to get index stats: {e}")
            return {}
