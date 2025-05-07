"""
Routes for managing conversations.
"""
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.animation import (
    ConversationResponse, 
    ConversationWithAnimations, 
    AnimationHistoryResponse,
    CreateConversationRequest,
    ConversationSidebarResponse,
    RenameConversationRequest
)
from app.services.conversation_service import (
    get_user_conversations, 
    get_conversation_with_animations,
    create_conversation,
    get_conversation_sidebar_data,
    rename_conversation,
    delete_conversation
)

router = APIRouter(prefix="/api", tags=["conversation"])


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
async def start_new_conversation(
    request: CreateConversationRequest,
    db: AsyncSession = Depends(get_db)
) -> ConversationResponse:
    """
    Create a new conversation.
    
    Args:
        request: Request containing user_id, optional title and initial_prompt
        db: Database session
        
    Returns:
        ConversationResponse: The created conversation
    """
    try:
        conversation = await create_conversation(
            db=db,
            user_id=request.user_id,
            title=request.title,
            initial_prompt=request.initial_prompt
        )
        
        # Commit the transaction to save the conversation
        await db.commit()
        
        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
    except Exception as e:
        # Roll back the transaction in case of errors
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create conversation: {str(e)}"
        )


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


@router.get("/sidebar", response_model=List[ConversationSidebarResponse])
async def get_conversation_sidebar(
    user_id: UUID,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
) -> List[ConversationSidebarResponse]:
    """
    Get optimized conversation data for sidebar display.
    
    Args:
        current_user: The authenticated user
        skip: Number of conversations to skip (pagination)
        limit: Maximum number of conversations to return (1-100)
        db: Database session
        
    Returns:
        List of conversation sidebar data
    """
    return await get_conversation_sidebar_data(
        db=db,
        user_id=user_id,
        skip=skip,
        limit=limit
    ) 


@router.patch("/conversations/{conversation_id}/rename", response_model=ConversationResponse)
async def rename_conversation_route(
    conversation_id: UUID,
    request: RenameConversationRequest,
    db: AsyncSession = Depends(get_db)
) -> ConversationResponse:
    """
    Rename a conversation.
    
    Args:
        conversation_id: ID of the conversation to rename
        request: Request containing user_id and new_title
        db: Database session
        
    Returns:
        Updated conversation
        
    Raises:
        HTTPException: If the conversation is not found or not owned by the user
    """
    try:
        conversation = await rename_conversation(
            db=db,
            conversation_id=conversation_id,
            user_id=request.user_id,
            new_title=request.new_title
        )
        
        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conversation_id} not found or not owned by the user"
            )
        
        # Commit the transaction
        await db.commit()
        
        return ConversationResponse(
            id=conversation.id,
            user_id=conversation.user_id,
            title=conversation.title,
            created_at=conversation.created_at,
            updated_at=conversation.updated_at
        )
    except Exception as e:
        # Roll back the transaction in case of errors
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to rename conversation: {str(e)}"
        )


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_conversation_route(
    conversation_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    """
    Delete a conversation and all its animations.
    
    Args:
        conversation_id: ID of the conversation to delete
        user_id: ID of the user who owns the conversation
        db: Database session
        
    Raises:
        HTTPException: If the conversation is not found or not owned by the user
    """
    try:
        success = await delete_conversation(
            db=db,
            conversation_id=conversation_id,
            user_id=user_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation with ID {conversation_id} not found or not owned by the user"
            )
        
        # Commit the transaction
        await db.commit()
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Roll back the transaction in case of errors
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete conversation: {str(e)}"
        ) 