"""
Service for managing conversations and animations in the database.
"""
import uuid
from typing import List, Optional, Tuple, Dict, Any
from uuid import UUID

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.db_models import Conversation, Animation, Message
from app.models.animation import ConversationSidebarResponse, QualityOption, AnimationStatus


async def create_conversation(
    db: AsyncSession,
    user_id: UUID,
    title: Optional[str] = None,
    initial_prompt: Optional[str] = None
) -> Conversation:
    """
    Create a new conversation.
    
    Args:
        db: Database session
        user_id: UUID of the user who owns the conversation
        title: Optional title for the conversation
        initial_prompt: Optional first prompt to generate a title from
        
    Returns:
        Conversation: The created conversation
    """
    # Generate a title if none is provided
    if not title and initial_prompt:
        title = generate_conversation_title(initial_prompt)
    elif not title:
        title = f"Conversation {uuid.uuid4().hex[:8]}"
    
    # Create the conversation
    conversation = Conversation(
        user_id=user_id,
        title=title
    )
    db.add(conversation)
    await db.flush()
    
    return conversation


def generate_conversation_title(prompt: str) -> str:
    """
    Generate a conversation title from a prompt.
    
    In a production application, this could use an LLM to generate a more meaningful title.
    
    Args:
        prompt: The initial prompt
        
    Returns:
        str: A generated title
    """
    # Simple implementation: use the first few words of the prompt
    words = prompt.strip().split()
    if len(words) <= 5:
        title = prompt.strip()
    else:
        title = " ".join(words[:5]) + "..."
    
    # Capitalize the first letter of the title
    if title:
        title = title[0].upper() + title[1:]
    
    return title


async def get_or_create_conversation(
    db: AsyncSession, 
    conversation_id: Optional[UUID], 
    user_id: UUID,
    title: Optional[str] = None
) -> Conversation:
    """
    Get an existing conversation or create a new one if it doesn't exist.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation to get, or None to create a new one
        user_id: UUID of the user who owns the conversation
        title: Optional title for the conversation
        
    Returns:
        Conversation: The found or created conversation
        
    Raises:
        ValueError: If the conversation does not exist or belongs to a different user
    """
    if conversation_id:
        # Try to get the existing conversation
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        result = await db.execute(query)
        conversation = result.scalar_one_or_none()
        
        if not conversation:
            raise ValueError(f"Conversation with ID {conversation_id} not found or belongs to a different user")
        
        return conversation
    else:
        # Create a new conversation
        conversation = Conversation(
            user_id=user_id,
            title=title or f"Conversation {uuid.uuid4().hex[:8]}"
        )
        db.add(conversation)
        await db.flush()
        return conversation


async def save_animation(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    query: str,
    generated_code: str,
    video_url: str,
    quality: QualityOption,
    success: bool = True,
    error_message: Optional[str] = None,
    status: Optional[AnimationStatus] = None,
    progress: float = 0.0,
    status_message: Optional[str] = None
) -> Animation:
    """
    Save a generated animation to the database.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation this animation belongs to
        user_id: UUID of the user who requested the animation
        query: The natural language query used to generate the animation
        generated_code: The generated Manim code
        video_url: URL to the generated video
        quality: Quality level used for rendering
        success: Whether the animation generation was successful
        error_message: Error message if the generation failed
        status: Current processing status
        progress: Current progress percentage (0-100)
        status_message: Optional status message
        
    Returns:
        Animation: The created animation record
    """
    # Calculate the new version number
    query = select(func.max(Animation.version)).where(
        Animation.conversation_id == conversation_id
    )
    result = await db.execute(query)
    max_version = result.scalar_one_or_none() or 0
    
    # Create and save the new animation
    animation = Animation(
        conversation_id=conversation_id,
        user_id=user_id,
        query=query,
        generated_code=generated_code,
        video_url=video_url,
        version=max_version + 1,
        quality=quality,
        success=success,
        error_message=error_message,
        status=status or AnimationStatus.PENDING,
        progress=progress,
        status_message=status_message
    )
    
    db.add(animation)
    await db.flush()
    return animation


async def get_conversation_with_animations(
    db: AsyncSession, 
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Dict[str, Any]]:
    """
    Get a conversation and all its animations.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation to get
        user_id: UUID of the user who owns the conversation
        
    Returns:
        Optional[Dict[str, Any]]: The conversation data and animations, or None if not found
    """
    query = (
        select(Conversation)
        .options(selectinload(Conversation.animations))
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    )
    
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        return None
    
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "animations": [
            {
                "id": anim.id,
                "query": anim.query,
                "video_url": anim.video_url,
                "version": anim.version,
                "quality": anim.quality,
                "success": anim.success,
                "created_at": anim.created_at,
                "status": anim.status,
                "progress": anim.progress,
                "status_message": anim.status_message
            }
            for anim in sorted(conversation.animations, key=lambda x: x.created_at)
        ]
    }


async def get_conversation_with_messages_and_animations(
    db: AsyncSession, 
    conversation_id: UUID,
    user_id: UUID
) -> Optional[Dict[str, Any]]:
    """
    Get a conversation with all its messages and animations.
    
    Args:
        db: Database session
        conversation_id: UUID of the conversation to get
        user_id: UUID of the user who owns the conversation
        
    Returns:
        Optional[Dict[str, Any]]: The conversation data with messages and animations, or None if not found
    """
    query = (
        select(Conversation)
        .options(
            selectinload(Conversation.animations),
            selectinload(Conversation.messages)
        )
        .where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
    )
    
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        return None
    
    return {
        "id": conversation.id,
        "user_id": conversation.user_id,
        "title": conversation.title,
        "created_at": conversation.created_at,
        "updated_at": conversation.updated_at,
        "animations": [
            {
                "id": anim.id,
                "query": anim.query,
                "video_url": anim.video_url,
                "version": anim.version,
                "quality": anim.quality,
                "success": anim.success,
                "created_at": anim.created_at,
                "status": anim.status,
                "progress": anim.progress,
                "status_message": anim.status_message
            }
            for anim in sorted(conversation.animations, key=lambda x: x.created_at)
        ],
        "messages": [
            {
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "content": msg.content,
                "type": msg.type,
                "animation_id": msg.animation_id,
                "created_at": msg.created_at
            }
            for msg in sorted(conversation.messages, key=lambda x: x.created_at)
        ]
    }


async def get_user_conversations(
    db: AsyncSession, 
    user_id: UUID, 
    skip: int = 0, 
    limit: int = 100
) -> Tuple[List[Dict[str, Any]], int]:
    """
    Get a list of conversations for a user.
    
    Args:
        db: Database session
        user_id: UUID of the user
        skip: Number of conversations to skip (pagination)
        limit: Maximum number of conversations to return
        
    Returns:
        Tuple[List[Dict[str, Any]], int]: List of conversations and total count
    """
    # Get total count
    count_query = select(func.count()).where(Conversation.user_id == user_id)
    count_result = await db.execute(count_query)
    total_count = count_result.scalar_one()
    
    # Get paginated conversations
    query = (
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .order_by(Conversation.updated_at.desc())
        .offset(skip).limit(limit)
    )
    
    result = await db.execute(query)
    conversations = result.scalars().all()
    
    return [
        {
            "id": conv.id,
            "user_id": conv.user_id,
            "title": conv.title,
            "created_at": conv.created_at,
            "updated_at": conv.updated_at
        }
        for conv in conversations
    ], total_count


async def get_conversation_sidebar_data(
    db: AsyncSession,
    user_id: UUID,
    skip: int = 0,
    limit: int = 50
) -> List[ConversationSidebarResponse]:
    """
    Get optimized conversation data for sidebar display.
    
    Args:
        db: Database session
        user_id: The ID of the user
        skip: Number of conversations to skip (pagination)
        limit: Maximum number of conversations to return
        
    Returns:
        List of conversation sidebar data
    """
    # Query conversations with animation count and message count
    query = select(
        Conversation,
        func.count(Animation.id).label('animation_count'),
        func.count(Message.id).label('message_count')
    ).outerjoin(
        Animation,
        Animation.conversation_id == Conversation.id
    ).outerjoin(
        Message,
        Message.conversation_id == Conversation.id
    ).where(
        Conversation.user_id == user_id
    ).group_by(
        Conversation.id
    ).order_by(
        Conversation.updated_at.desc()
    ).offset(skip).limit(limit)
    
    result = await db.execute(query)
    conversations = result.all()
    
    # Generate preview text from latest message if available
    sidebar_data = []
    for conv, anim_count, msg_count in conversations:
        # Get latest message for preview
        preview_query = select(Message).where(
            Message.conversation_id == conv.id
        ).order_by(Message.created_at.desc()).limit(1)
        
        preview_result = await db.execute(preview_query)
        latest_message = preview_result.scalar_one_or_none()
        
        preview = None
        if latest_message:
            # Truncate content to a reasonable length for preview
            if len(latest_message.content) > 50:
                preview = latest_message.content[:50] + "..."
            else:
                preview = latest_message.content
        
        # Add to response data
        sidebar_data.append(
            ConversationSidebarResponse(
                id=conv.id,
                title=conv.title,
                last_active=conv.updated_at,
                preview=preview,
                animation_count=anim_count,
                message_count=msg_count
            )
        )
    
    return sidebar_data


async def rename_conversation(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID,
    new_title: str
) -> Optional[Conversation]:
    """
    Rename a conversation.
    
    Args:
        db: Database session
        conversation_id: ID of the conversation to rename
        user_id: ID of the user who owns the conversation
        new_title: New title for the conversation
        
    Returns:
        Updated conversation or None if not found or not owned by the user
    """
    # Find the conversation
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        return None
    
    # Update the title
    conversation.title = new_title
    conversation.updated_at = func.now()
    
    db.add(conversation)
    await db.flush()
    
    return conversation


async def delete_conversation(
    db: AsyncSession,
    conversation_id: UUID,
    user_id: UUID
) -> bool:
    """
    Delete a conversation and all its animations.
    
    Args:
        db: Database session
        conversation_id: ID of the conversation to delete
        user_id: ID of the user who owns the conversation
        
    Returns:
        True if deleted successfully, False if not found or not owned by the user
    """
    # Find the conversation
    query = select(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    result = await db.execute(query)
    conversation = result.scalar_one_or_none()
    
    if not conversation:
        return False
    
    # Delete all messages in the conversation
    delete_messages = delete(Message).where(
        Message.conversation_id == conversation_id
    )
    await db.execute(delete_messages)
    
    # Delete all animations in the conversation
    delete_animations = delete(Animation).where(
        Animation.conversation_id == conversation_id
    )
    await db.execute(delete_animations)
    
    # Delete the conversation
    delete_conv = delete(Conversation).where(
        Conversation.id == conversation_id,
        Conversation.user_id == user_id
    )
    await db.execute(delete_conv)
    
    return True 