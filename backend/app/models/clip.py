from sqlalchemy import Column, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Clip(Base):
    __tablename__ = "clips"

    id = Column(String, primary_key=True)
    video_id = Column(String, ForeignKey("videos.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Clip timing
    start_time = Column(Float, nullable=False)
    end_time = Column(Float, nullable=False)
    
    # AI-generated metadata
    transcript = Column(Text)
    scene_type = Column(String)
    thumbnail_url = Column(String)
    
    # Vector embedding reference
    embedding_id = Column(String)  # Reference to Pinecone vector ID
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    
    # Relationships
    video = relationship("Video", back_populates="clips")
    compilation_associations = relationship("CompilationClip", back_populates="clip")
