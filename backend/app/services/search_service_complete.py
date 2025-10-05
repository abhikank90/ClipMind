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

# Import storage and repositories
from app.storage.s3_service import S3Service
from app.repositories.video_repository import VideoRepository
from app.repositories.clip_repository import ClipRepository
from app.repositories.search_repository import SearchRepository
from app.db.session import get_db

logger = logging.getLogger(__name__)


class SearchService:
    def __init__(self):
        # Initialize AI models (lazy loading in production)
        self._clip_model = None
        self._text_embedder = None
        self._pinecone_client = None
        self._s3_service = None
    
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
    
    @property
    def s3_service(self):
        if self._s3_service is None:
            self._s3_service = S3Service()
        return self._s3_service
    
    async def search(
        self,
        query: str,
        user_id: str,
        filters: Optional[SearchFilters] = None,
        limit: int = 20
    ) -> SearchResponse:
        """
        Complete AI-powered semantic search with database enrichment
        
        Flow:
        1. Generate query embeddings (CLIP + Sentence-BERT)
        2. Search Pinecone for similar vectors
        3. Enrich with PostgreSQL data (video titles, thumbnails)
        4. Generate presigned S3 URLs
        5. Save search query and results for analytics
        6. Return complete results
        """
        try:
            start_time = time.time()
            search_id = f"search_{int(time.time())}_{user_id[:8]}"
            
            logger.info(f"AI-powered search: '{query}' by user {user_id}")
            
            # STEP 1: Generate query embeddings
            logger.debug("Generating query embeddings")
            clip_embedding = self.clip_model.encode_text(query)
            text_embedding = self.text_embedder.encode(query)
            
            # STEP 2: Search Pinecone
            logger.debug("Searching Pinecone")
            
            # Build filter for Pinecone
            pinecone_filter = {'user_id': user_id}
            if filters and filters.video_ids:
                pinecone_filter['video_id'] = {'$in': filters.video_ids}
            
            # Search with visual embedding
            visual_results = self.pinecone_client.query(
                query_vector=clip_embedding,
                top_k=limit * 2,  # Get more for merging
                filter=pinecone_filter
            )
            
            # Search with text embedding
            text_results = self.pinecone_client.query(
                query_vector=text_embedding,
                top_k=limit * 2,
                filter=pinecone_filter
            )
            
            # STEP 3: Merge and rank results
            merged_results = self._merge_results(visual_results, text_results, limit)
            
            # STEP 4: Enrich with database data
            logger.debug("Enriching with database data")
            enriched_clips = await self._enrich_results(merged_results, user_id)
            
            processing_time = (time.time() - start_time) * 1000
            
            # STEP 5: Save search query for analytics
            db = next(get_db())
            try:
                search_repo = SearchRepository(db)
                
                # Save query
                search_repo.create_search_query(
                    search_id=search_id,
                    user_id=user_id,
                    query_text=query,
                    results_count=len(enriched_clips),
                    processing_time_ms=processing_time
                )
                
                # Save results
                results_for_analytics = [
                    {
                        'clip_id': clip.clip_id,
                        'relevance_score': clip.relevance_score
                    }
                    for clip in enriched_clips
                ]
                search_repo.save_search_results(search_id, results_for_analytics)
                
            finally:
                db.close()
            
            logger.info(f"Search completed: {len(enriched_clips)} results in {processing_time:.2f}ms")
            
            return SearchResponse(
                query=query,
                total_results=len(enriched_clips),
                clips=enriched_clips,
                processing_time_ms=processing_time,
                search_id=search_id  # Include for tracking
            )
            
        except Exception as e:
            logger.error(f"Search error: {str(e)}", exc_info=True)
            raise SearchException(f"Search failed: {str(e)}")
    
    async def _enrich_results(
        self,
        pinecone_results: List[Dict],
        user_id: str
    ) -> List[ClipResult]:
        """
        Enrich Pinecone results with PostgreSQL data and S3 URLs
        
        Returns complete ClipResult objects with:
        - Real video titles
        - Real thumbnail URLs (presigned)
        - Playback URLs (presigned)
        - Complete transcript
        - All metadata
        """
        db = next(get_db())
        try:
            video_repo = VideoRepository(db)
            clip_repo = ClipRepository(db)
            
            enriched_clips = []
            
            for result in pinecone_results:
                metadata = result['metadata']
                clip_id_base = result['id'].rsplit('_', 2)[0]  # Remove _visual_N or _text_N
                
                # Get clip from database
                clip = clip_repo.get_by_id(clip_id_base)
                if not clip:
                    logger.warning(f"Clip not found in DB: {clip_id_base}")
                    continue
                
                # Get video from database
                video = video_repo.get_by_id(clip.video_id)
                if not video:
                    logger.warning(f"Video not found in DB: {clip.video_id}")
                    continue
                
                # Verify ownership
                if video.user_id != user_id:
                    continue
                
                # Generate presigned URLs
                thumbnail_url = None
                if clip.thumbnail_url:
                    thumbnail_url = self.s3_service.get_video_url(clip.thumbnail_url)
                elif video.thumbnail_url:
                    thumbnail_url = self.s3_service.get_video_url(video.thumbnail_url)
                
                # Generate clip playback URL
                # For now, use video URL with timestamp
                # In production, you'd extract the actual clip
                video_url = self.s3_service.get_video_url(video.s3_key)
                clip_url = f"{video_url}#t={clip.start_time},{clip.end_time}"
                
                enriched_clips.append(ClipResult(
                    clip_id=clip.id,
                    video_id=video.id,
                    video_title=video.title,
                    start_time=clip.start_time,
                    end_time=clip.end_time,
                    relevance_score=result['score'],
                    thumbnail_url=thumbnail_url,
                    transcript=clip.transcript or "",
                    clip_url=clip_url,  # Presigned playback URL
                    duration=clip.end_time - clip.start_time,
                    created_at=clip.created_at
                ))
            
            return enriched_clips
            
        finally:
            db.close()
    
    def _merge_results(
        self,
        visual_results: List[Dict],
        text_results: List[Dict],
        limit: int
    ) -> List[Dict]:
        """Merge and rank visual and text search results"""
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
                combined[result['id']]['score'] += result['score'] * 0.4
            else:
                combined[result['id']] = {
                    **result,
                    'score': result['score'] * 0.4
                }
        
        # Sort and limit
        sorted_results = sorted(
            combined.values(),
            key=lambda x: x['score'],
            reverse=True
        )
        
        return sorted_results[:limit]
    
    async def get_search_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Get user's search history"""
        db = next(get_db())
        try:
            search_repo = SearchRepository(db)
            history = search_repo.get_user_search_history(user_id, limit)
            
            return [
                {
                    'search_id': h.id,
                    'query': h.query_text,
                    'results_count': h.results_count,
                    'processing_time_ms': h.processing_time_ms,
                    'created_at': h.created_at.isoformat()
                }
                for h in history
            ]
        finally:
            db.close()
    
    async def track_clip_view(
        self,
        user_id: str,
        clip_id: str,
        search_query_id: Optional[str] = None,
        duration_seconds: Optional[float] = None
    ) -> bool:
        """Track when user views a clip"""
        db = next(get_db())
        try:
            search_repo = SearchRepository(db)
            interaction_id = f"interaction_{int(time.time())}_{user_id[:8]}"
            
            search_repo.track_interaction(
                interaction_id=interaction_id,
                user_id=user_id,
                clip_id=clip_id,
                action="viewed",
                search_query_id=search_query_id,
                duration_seconds=duration_seconds
            )
            
            return True
        except Exception as e:
            logger.error(f"Failed to track interaction: {e}")
            return False
        finally:
            db.close()
