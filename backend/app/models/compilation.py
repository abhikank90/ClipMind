from sqlalchemy import Column, String, Float, Integer, DateTime, ForeignKey, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.models.base import Base

class Compilation(Base):
    __tablename__ = "compilations"

    id = Column(String, primary_key=True)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    
    title = Column(String, nullable=False)
    description = Column(Text)
    
    # Compilation metadata
    status = Column(String, nullable=False, default="draft")  # draft, rendering, rendered, failed
    duration = Column(Float)
    output_url = Column(String)
    thumbnail_url = Column(String)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    rendered_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="compilations")
    clip_associations = relationship("CompilationClip", back_populates="compilation", cascade="all, delete-orphan")


class CompilationClip(Base):
    __tablename__ = "compilation_clips"

    compilation_id = Column(String, ForeignKey("compilations.id", ondelete="CASCADE"), primary_key=True)
    clip_id = Column(String, ForeignKey("clips.id", ondelete="CASCADE"), primary_key=True)
    
    order = Column(Integer, nullable=False)
    transition = Column(String)  # fade, cut, dissolve, etc.
    
    # Relationships
    compilation = relationship("Compilation", back_populates="clip_associations")
    clip = relationship("Clip", back_populates="compilation_associations")
