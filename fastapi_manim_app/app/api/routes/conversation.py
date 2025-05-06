"""
Routes for managing conversations.
"""
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.animation import ConversationResponse, ConversationWithAnimations, AnimationHistoryResponse
from app.services.conversation_service import get_user_conversations, get_conversation_with_animations

router = APIRouter(prefix="/api", tags=["conversation"])


@router.get("/conversations", response_model=list[ConversationResponse])
async def list_conversations(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
) -> list[ConversationResponse]:
    """
    List all conversations for a user.
    
    Args:
        user_id: ID of the user
        skip: Number of conversations to skip (pagination)
        limit: Maximum number of conversations to return
        db: Database session
        
    Returns:
        List[ConversationResponse]: List of conversations
    """
    conversations, _ = await get_user_conversations(db, user_id, skip, limit)
    return conversations


@router.get("/conversations/{conversation_id}", response_model=ConversationWithAnimations)
async def get_conversation(
    conversation_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> ConversationWithAnimations:
    """
    Get a conversation with all its animations.
    
    Args:
        conversation_id: ID of the conversation to get
        user_id: ID of the user who owns the conversation
        db: Database session
        
    Returns:
        ConversationWithAnimations: Conversation with its animations
        
    Raises:
        HTTPException: If the conversation is not found
    """
    conversation = await get_conversation_with_animations(db, conversation_id, user_id)
    if not conversation:
        raise HTTPException(
            status_code=404,
            detail=f"Conversation with ID {conversation_id} not found"
        )
    
    return conversation 