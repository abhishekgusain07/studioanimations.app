"""
Routes for generating Manim animations.
"""
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.models.animation import AnimationRequest, AnimationResponse, QualityOption, AnimationHistoryResponse
from app.services.manim_service import generate_animation_from_query
from app.services.conversation_service import get_conversation_with_animations, create_conversation

router = APIRouter(prefix="/api", tags=["animation"])


class AnimationRequest(BaseModel):
    """Request model for animation generation."""
    query: str
    quality: QualityOption = QualityOption.LOW
    conversation_id: UUID = None
    user_id: UUID
    previous_code: str = None


class AnimationResponse(BaseModel):
    """Response model for animation generation."""
    id: UUID
    success: bool
    video_url: str = ""
    message: str = ""
    conversation_id: UUID = None
    user_id: UUID
    version: int
    created_at: str = None


@router.post("/generate-animation", response_model=AnimationResponse)
async def generate_animation(
    request: AnimationRequest,
    db: AsyncSession = Depends(get_db)
) -> AnimationResponse:
    """
    Generate a Manim animation based on a user query.
    
    Args:
        request: Animation request containing:
            - query: Description of the animation to generate
            - quality: Video quality setting (low, medium, high)
              Low quality is faster to render but less detailed.
              Medium quality offers a balance between speed and detail.
              High quality produces the best visual results but takes longer to render.
            - conversation_id: Optional ID of the conversation this animation belongs to
            - user_id: ID of the user making the request
            - previous_code: Optional code from a previous animation to use as a base
        db: Database session
        
    Returns:
        AnimationResponse: Response containing success status and video URL
        
    Raises:
        HTTPException: If animation generation fails
    """
    try:
        # Create a new conversation if one isn't provided
        if not request.conversation_id:
            conversation = await create_conversation(
                db=db,
                user_id=request.user_id,
                initial_prompt=request.query
            )
            await db.flush()
            conversation_id = conversation.id
        else:
            conversation_id = request.conversation_id

        # Generate the animation - message will be saved by the service
        success, video_url, error_msg, animation_id, conversation_id = await generate_animation_from_query(
            query=request.query,
            quality=request.quality,
            conversation_id=conversation_id,
            user_id=request.user_id,
            previous_code=request.previous_code,
            db=db
        )
        
        # Commit the transaction
        await db.commit()
        
        if not success:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_msg or "Failed to generate animation"
            )
        
        # Get the version of the created animation
        conversation_data = await get_conversation_with_animations(db, conversation_id, request.user_id)
        animation = next((a for a in conversation_data["animations"] if str(a["id"]) == str(animation_id)), None)
        version = animation["version"] if animation else 1
        created_at = animation["created_at"] if animation else None
        
        return AnimationResponse(
            id=animation_id,
            success=True,
            video_url=video_url,
            message="Animation generated successfully",
            conversation_id=conversation_id,
            user_id=request.user_id,
            version=version,
            created_at=created_at
        )
    except HTTPException:
        # Re-raise HTTP exceptions as-is
        raise
    except Exception as e:
        # Roll back the transaction in case of errors
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating animation: {str(e)}"
        )


@router.get("/animations", response_model=AnimationHistoryResponse)
async def get_animations(
    user_id: UUID,
    conversation_id: UUID = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
) -> AnimationHistoryResponse:
    """
    Get a list of animations for a user, optionally filtered by conversation.
    
    Args:
        user_id: ID of the user
        conversation_id: Optional ID of the conversation to filter by
        skip: Number of animations to skip (pagination)
        limit: Maximum number of animations to return
        db: Database session
        
    Returns:
        AnimationHistoryResponse: List of animations and count
    """
    if conversation_id:
        # Get animations for a specific conversation
        conversation_data = await get_conversation_with_animations(db, conversation_id, user_id)
        if not conversation_data:
            raise HTTPException(
                status_code=404,
                detail=f"Conversation with ID {conversation_id} not found"
            )
        
        # Apply pagination
        animations = conversation_data["animations"][skip:skip+limit]
        total_count = len(conversation_data["animations"])
    else:
        # Get all animations for a user
        # This would require a new service function that we haven't implemented yet
        # For simplicity, we'll return an empty list for now
        animations = []
        total_count = 0
    
    return AnimationHistoryResponse(
        animations=animations,
        count=total_count
    ) 