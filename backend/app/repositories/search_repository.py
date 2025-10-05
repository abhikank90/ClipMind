from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import List, Optional
from datetime import datetime
import time

from app.models.search_query import SearchQuery, SearchResult, ClipInteraction
import logging

logger = logging.getLogger(__name__)


class SearchRepository:
    def __init__(self, db: Session):
        self.db = db
    
    def create_search_query(
        self,
        search_id: str,
        user_id: str,
        query_text: str,
        results_count: int,
        processing_time_ms: float
    ) -> SearchQuery:
        """Save search query to database"""
        search_query = SearchQuery(
            id=search_id,
            user_id=user_id,
            query_text=query_text,
            results_count=results_count,
            processing_time_ms=processing_time_ms
        )
        
        self.db.add(search_query)
        self.db.commit()
        self.db.refresh(search_query)
        
        logger.info(f"Search query saved: {search_id}")
        return search_query
    
    def save_search_results(
        self,
        search_query_id: str,
        results: List[dict]
    ) -> List[SearchResult]:
        """Save search results for analytics"""
        search_results = []
        
        for rank, result in enumerate(results, start=1):
            result_id = f"{search_query_id}_result_{rank}"
            
            search_result = SearchResult(
                id=result_id,
                search_query_id=search_query_id,
                clip_id=result['clip_id'],
                rank=rank,
                relevance_score=result['relevance_score']
            )
            
            search_results.append(search_result)
        
        self.db.add_all(search_results)
        self.db.commit()
        
        logger.info(f"Saved {len(search_results)} search results")
        return search_results
    
    def get_user_search_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[SearchQuery]:
        """Get user's search history"""
        return (
            self.db.query(SearchQuery)
            .filter(SearchQuery.user_id == user_id)
            .order_by(desc(SearchQuery.created_at))
            .limit(limit)
            .all()
        )
    
    def track_interaction(
        self,
        interaction_id: str,
        user_id: str,
        clip_id: str,
        action: str,
        search_query_id: Optional[str] = None,
        duration_seconds: Optional[float] = None
    ) -> ClipInteraction:
        """Track user interaction with clip"""
        interaction = ClipInteraction(
            id=interaction_id,
            user_id=user_id,
            clip_id=clip_id,
            search_query_id=search_query_id,
            action=action,
            duration_seconds=duration_seconds
        )
        
        self.db.add(interaction)
        self.db.commit()
        self.db.refresh(interaction)
        
        logger.info(f"Interaction tracked: {action} on clip {clip_id}")
        return interaction
    
    def get_popular_clips(
        self,
        user_id: str,
        days: int = 7,
        limit: int = 10
    ) -> List[dict]:
        """Get most viewed clips for user in last N days"""
        from datetime import timedelta
        from sqlalchemy import func
        
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        results = (
            self.db.query(
                ClipInteraction.clip_id,
                func.count(ClipInteraction.id).label('view_count')
            )
            .filter(
                and_(
                    ClipInteraction.user_id == user_id,
                    ClipInteraction.action == 'viewed',
                    ClipInteraction.created_at >= cutoff_date
                )
            )
            .group_by(ClipInteraction.clip_id)
            .order_by(desc('view_count'))
            .limit(limit)
            .all()
        )
        
        return [
            {'clip_id': r.clip_id, 'view_count': r.view_count}
            for r in results
        ]
