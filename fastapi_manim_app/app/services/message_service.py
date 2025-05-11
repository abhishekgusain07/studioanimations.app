"""
Service for managing messages in conversations.
"""
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Message, MessageType
from app.models.animation import MessageResponse


async def create_message(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    content: str,
    message_type: MessageType,
    animation_id: Optional[UUID] = None
) -> Message:
    """
    Create a new message in a conversation.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        user_id: UUID of the user
        content: Message content
        message_type: Type of message (user or ai)
        animation_id: Optional UUID of related animation for AI messages
        
    Returns:
        Message: The created message
    """
    message = Message(
        conversation_id=conversation_id,
        user_id=user_id,
        content=content,
        type=message_type,
        animation_id=animation_id
    )
    
    db.add(message)
    await db.flush()
    
    return message


async def get_conversation_messages(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    skip: int = 0,
    limit: int = 100
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Get all messages in a conversation.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        user_id: UUID of the user who owns the conversation
        skip: Number of messages to skip (pagination)
        limit: Maximum number of messages to return
        
    Returns:
        Tuple[List[Dict[str, Any]], int]: List of messages and total count
    """
    # Get total count
    count_query = select(func.count()).select_from(Message).where(
        Message.conversation_id == conversation_id,
        Message.user_id == user_id
    )
    count_result = await db.execute(count_query)
    total_count = count_result.scalar_one()
    
    # Get paginated messages
    query = select(Message).where(
        Message.conversation_id == conversation_id,
        Message.user_id == user_id
    ).order_by(
        Message.created_at
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    messages = result.scalars().all()
    
    return [
        {
            "id": msg.id,
            "conversation_id": msg.conversation_id,
            "content": msg.content,
            "type": msg.type,
            "animation_id": msg.animation_id,
            "created_at": msg.created_at
        }
        for msg in messages
    ], total_count


async def delete_conversation_messages(
    db: AsyncSession,
    conversation_id: UUID
) -> int:
    """
    Delete all messages in a conversation.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation
        
    Returns:
        int: Number of messages deleted
    """
    query = delete(Message).where(
        Message.conversation_id == conversation_id
    )
    result = await db.execute(query)
    return result.rowcount 