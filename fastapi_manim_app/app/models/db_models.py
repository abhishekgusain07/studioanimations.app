"""
Database models for the application.
"""
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import (
    Column, 
    String, 
    Text, 
    DateTime, 
    ForeignKey, 
    Boolean, 
    Integer,
    func,
    Enum,
    Float
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum

from app.core.database import Base


class MessageType(str, enum.Enum):
    """Enum for message types."""
    USER = "user"
    AI = "ai"


class Conversation(Base):
    """Model for tracking conversations."""
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    title = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    animations = relationship("Animation", back_populates="conversation", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    def __repr__(self) -> str:
        return f"<Conversation(id={self.id}, user_id={self.user_id}, title={self.title})>"


class AnimationStatus(str, enum.Enum):
    """Enum for animation processing status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class Animation(Base):
    """Model for storing animation data."""
    __tablename__ = "animations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    query = Column(Text, nullable=False)
    generated_code = Column(Text, nullable=False)
    video_url = Column(String(255), nullable=False)
    version = Column(Integer, default=1)
    quality = Column(String(10), nullable=False, default="low")
    success = Column(Boolean, default=True)
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Progress tracking
    status = Column(Enum(AnimationStatus), nullable=False, default=AnimationStatus.PENDING)
    progress = Column(Float, nullable=False, default=0.0)  # 0.0 to 100.0 percent
    status_message = Column(Text, nullable=True)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="animations")
    
    def __repr__(self) -> str:
        return f"<Animation(id={self.id}, conversation_id={self.conversation_id}, version={self.version})>"


class Message(Base):
    """Model for storing messages in a conversation."""
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user_id = Column(UUID(as_uuid=True), nullable=False, index=True)
    content = Column(Text, nullable=False)
    type = Column(Enum(MessageType), nullable=False)
    animation_id = Column(
        UUID(as_uuid=True),
        ForeignKey("animations.id", ondelete="SET NULL"),
        nullable=True
    )
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self) -> str:
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, type={self.type})>" 