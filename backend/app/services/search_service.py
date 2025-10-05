import logging
import time
from typing import List, Optional, Dict, Any

from app.schemas.search import SearchResponse, ClipResult, SearchFilters
from app.core.exceptions import SearchException
from app.core.config import settings

# Import AI models
from app.ai.clip_model import CLIPEmbedder
from app.ai.sentence_bert import SentenceBERTEmbedder
from app.search.pinecone_client import PineconeClient

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        # Initialize AI models (lazy loading in production)
        self._clip_model = None
        self._text_embedder = None
        self._pinecone_client = None
    
    @property
    def clip_model(self):
        if self._clip_model is None:
            self._clip_model = CLIPEmbedder()
        return self._clip_model
    
    @property
    def text_embedder(self):
        if self._text_embedder is None:
            self._text_embedder = SentenceBERTEmbedder()
        return self._text_embedder
    
    @property
    def pinecone_client(self):
        if self._pinecone_client is None:
            self._pinecone_client = PineconeClient(
                api_key=settings.PINECONE_API_KEY,
                environment=settings.PINECONE_ENVIRONMENT,
                index_name=settings.PINECONE_INDEX_NAME
            )
        return self._pinecone_client
    
    async def search(
        self,
        query: str,
        user_id: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 20
    ) -> SearchResponse:
        """
        Perform AI-powered semantic search
        
        Uses:
        1. CLIP for visual-text matching
        2. Sentence-BERT for text-text matching
        3. Pinecone for vector similarity search
        """
        try:
            start_time = time.time()
            logger.info(f"AI-powered search: '{query}' by user {user_id}")
            
            # Step 1: Generate query embeddings
            # Try CLIP for visual search
            clip_embedding = self.clip_model.encode_text(query)
            
            # Also use text embedding for transcript search
            text_embedding = self.text_embedder.encode(query)
            
            # Step 2: Search Pinecone with visual embedding
            visual_results = self.pinecone_client.query(
                query_vector=clip_embedding,
                top_k=limit,
                filter={'type': 'visual'} if filters else None
            )
            
            # Step 3: Search Pinecone with text embedding
            text_results = self.pinecone_client.query(
                query_vector=text_embedding,
                top_k=limit,
                filter={'type': 'text'} if filters else None
            )
            
            # Step 4: Merge and rank results
            merged_results = self._merge_results(visual_results, text_results, limit)
            
            # Step 5: Convert to ClipResult format
            clips = []
            for result in merged_results:
                metadata = result['metadata']
                clips.append(ClipResult(
                    clip_id=result['id'],
                    video_id=metadata.get('video_id', 'unknown'),
                    video_title=f"Video {metadata.get('video_id', 'unknown')}",
                    start_time=metadata.get('start_time', 0.0),
                    end_time=metadata.get('end_time', 0.0),
                    relevance_score=result['score'],
                    thumbnail_url=f"https://via.placeholder.com/320x180?text={result['id']}",
                    transcript=metadata.get('text', ''),
                ))
            
            processing_time = (time.time() - start_time) * 1000
            
            logger.info(f"Search completed: {len(clips)} results in {processing_time:.2f}ms")
            
            return SearchResponse(
                query=query,
                total_results=len(clips),
                clips=clips,
                processing_time_ms=processing_time
            )
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}", exc_info=True)
            raise SearchException(f"Search failed: {str(e)}")
    
    def _merge_results(
        self,
        visual_results: List[Dict],
        text_results: List[Dict],
        limit: int
    ) -> List[Dict]:
        """Merge and rank visual and text search results"""
        # Combine results with weighted scores
        combined = {}
        
        # Visual results (weight: 0.6)
        for result in visual_results:
            combined[result['id']] = {
                **result,
                'score': result['score'] * 0.6
            }
        
        # Text results (weight: 0.4)
        for result in text_results:
            if result['id'] in combined:
                # Boost score if found in both
                combined[result['id']]['score'] += result['score'] * 0.4
            else:
                combined[result['id']] = {
                    **result,
                    'score': result['score'] * 0.4
                }
        
        # Sort by score and return top results
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return sorted_results[:limit]
    
    async def find_similar(
        self,
        clip_id: str,
        user_id: str,
        limit: int = 10
    ) -> List[ClipResult]:
        """Find similar clips using vector similarity"""
        try:
            # Get the clip's embedding from Pinecone
            # In production: fetch from database or Pinecone
            
            # For now, search similar clips
            # This would use the clip's existing embedding
            logger.info(f"Finding similar clips to {clip_id}")
            
            # Placeholder: would get actual clip embedding and search
            return []
            
        except Exception as e:
            logger.error(f"Similar search error: {str(e)}")
            return []
