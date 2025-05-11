"""
Models for animation-related data structures.
"""
from enum import Enum
from uuid import UUID, uuid4
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field

from app.models.db_models import MessageType


class QualityOption(str, Enum):
    """Animation quality options."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class AnimationRequest(BaseModel):
    """Request model for animation generation."""
    query: str
    quality: QualityOption = QualityOption.LOW
    conversation_id: Optional[UUID] = None
    user_id: UUID
    previous_code: Optional[str] = None


class AnimationResponse(BaseModel):
    """Response model for animation generation."""
    id: UUID
    success: bool
    video_url: str = ""
    message: str = ""
    conversation_id: UUID
    user_id: UUID
    version: int
    created_at: datetime


class MessageResponse(BaseModel):
    """Response model for message data."""
    id: UUID
    conversation_id: UUID
    content: str
    type: MessageType
    animation_id: Optional[UUID] = None
    created_at: datetime


class CreateMessageRequest(BaseModel):
    """Request model for creating a new message."""
    conversation_id: UUID
    user_id: UUID
    content: str
    type: MessageType
    animation_id: Optional[UUID] = None


class ConversationBase(BaseModel):
    """Base model for conversation data."""
    user_id: UUID
    title: Optional[str] = None


class CreateConversationRequest(BaseModel):
    """Request model for creating a new conversation."""
    user_id: UUID
    title: Optional[str] = None
    initial_prompt: Optional[str] = None


class ConversationCreate(ConversationBase):
    """Model for creating a new conversation."""
    pass


class ConversationResponse(ConversationBase):
    """Response model for conversation data."""
    id: UUID
    created_at: datetime
    updated_at: datetime


class AnimationInConversation(BaseModel):
    """Animation data to be included in conversation responses."""
    id: UUID
    query: str
    video_url: str
    version: int
    quality: str
    success: bool
    created_at: datetime


class ConversationWithAnimations(ConversationResponse):
    """Conversation with its animations."""
    animations: List[AnimationInConversation] = []


class ConversationWithMessages(ConversationResponse):
    """Conversation with its messages."""
    messages: List[MessageResponse] = []


class ConversationWithAnimationsAndMessages(ConversationResponse):
    """Conversation with both animations and messages."""
    animations: List[AnimationInConversation] = []
    messages: List[MessageResponse] = []


class AnimationHistoryResponse(BaseModel):
    """Response model for animation history."""
    animations: List[AnimationInConversation]
    count: int


class MessageHistoryResponse(BaseModel):
    """Response model for message history."""
    messages: List[MessageResponse]
    count: int


class ConversationSidebarResponse(BaseModel):
    """Response model for conversation sidebar data."""
    id: UUID
    title: str
    last_active: datetime
    preview: Optional[str] = None
    animation_count: int = 0
    message_count: int = 0


class RenameConversationRequest(BaseModel):
    """Request model for renaming a conversation."""
    user_id: UUID
    new_title: str 