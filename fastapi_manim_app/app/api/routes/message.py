"""
Routes for managing messages in conversations.
"""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.animation import (
    MessageResponse,
    CreateMessageRequest,
    MessageHistoryResponse,
)
from app.models.db_models import MessageType
from app.services.message_service import create_message, get_conversation_messages

router = APIRouter(prefix="/api", tags=["message"])


@router.post("/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
async def create_message_route(
    request: CreateMessageRequest,
    db: AsyncSession = Depends(get_db)
) -> MessageResponse:
    """
    Create a new message in a conversation.
    
    Args:
        request: Request containing conversation_id, user_id, content, type, and optional animation_id
        db: Database session
        
    Returns:
        MessageResponse: The created message
    """
    try:
        message = await create_message(
            db=db,
            conversation_id=request.conversation_id,
            user_id=request.user_id,
            content=request.content,
            message_type=request.type,
            animation_id=request.animation_id
        )
        
        # Commit the transaction to save the message
        await db.commit()
        
        return MessageResponse(
            id=message.id,
            conversation_id=message.conversation_id,
            content=message.content,
            type=message.type,
            animation_id=message.animation_id,
            created_at=message.created_at
        )
    except Exception as e:
        # Roll back the transaction in case of errors
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create message: {str(e)}"
        )


@router.get("/conversations/{conversation_id}/messages", response_model=MessageHistoryResponse)
async def get_conversation_messages_route(
    conversation_id: UUID,
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
) -> MessageHistoryResponse:
    """
    Get all messages in a conversation.
    
    Args:
        conversation_id: ID of the conversation
        user_id: ID of the user who owns the conversation
        skip: Number of messages to skip (pagination)
        limit: Maximum number of messages to return
        db: Database session
        
    Returns:
        MessageHistoryResponse: Messages in the conversation
    """
    messages, total_count = await get_conversation_messages(
        db=db,
        conversation_id=conversation_id,
        user_id=user_id,
        skip=skip,
        limit=limit
    )
    
    return MessageHistoryResponse(
        messages=messages,
        count=total_count
    ) 