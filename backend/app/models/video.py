from sqlalchemy import Column, String, Float, Integer, BigInteger, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Video(Base):
    __tablename__ = "videos"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    project_id = Column(String, ForeignKey("projects.id", ondelete="SET NULL"))
    
    title = Column(String)
    description = Column(Text)
    filename = Column(String, nullable=False)
    s3_key = Column(String, nullable=False)
    
    # Video metadata
    duration = Column(Float)
    size_bytes = Column(BigInteger)
    width = Column(Integer)
    height = Column(Integer)
    fps = Column(Float)
    codec = Column(String)
    
    # Processing status
    status = Column(String, nullable=False, default="pending", index=True)
    thumbnail_url = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    processed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="videos")
    project = relationship("Project", back_populates="videos")
    clips = relationship("Clip", back_populates="video", cascade="all, delete-orphan")
