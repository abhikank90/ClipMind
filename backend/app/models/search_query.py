from sqlalchemy import Column, String, Integer, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base


class SearchQuery(Base):
    __tablename__ = "search_queries"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    query_text = Column(Text, nullable=False)
    results_count = Column(Integer, default=0)
    processing_time_ms = Column(Float)
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="search_queries")
    results = relationship("SearchResult", back_populates="search_query", cascade="all, delete-orphan")


class SearchResult(Base):
    __tablename__ = "search_results"

    id = Column(String, primary_key=True)
    search_query_id = Column(String, ForeignKey("search_queries.id", ondelete="CASCADE"), nullable=False)
    clip_id = Column(String, ForeignKey("clips.id", ondelete="CASCADE"), nullable=False)
    rank = Column(Integer, nullable=False)
    relevance_score = Column(Float, nullable=False)
    
    # Relationships
    search_query = relationship("SearchQuery", back_populates="results")
    clip = relationship("Clip")


class ClipInteraction(Base):
    __tablename__ = "clip_interactions"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    clip_id = Column(String, ForeignKey("clips.id", ondelete="CASCADE"), nullable=False, index=True)
    search_query_id = Column(String, ForeignKey("search_queries.id", ondelete="SET NULL"))
    
    action = Column(String, nullable=False)  # viewed, played, saved, shared
    duration_seconds = Column(Float)  # How long they watched
    created_at = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User")
    clip = relationship("Clip")
