"""
Service functions for animation-related operations.
"""
from uuid import UUID
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.db_models import Animation
from app.models.animation import AnimationStatusResponse


async def get_animation_status(
    db: AsyncSession,
    animation_id: UUID,
    user_id: UUID
) -> Optional[AnimationStatusResponse]:
    """
    Get the current status of an animation.
    
    Args:
        db: Database session
        animation_id: ID of the animation to get status for
        user_id: ID of the user requesting the status
        
    Returns:
        AnimationStatusResponse: Current status, progress, and status message
        None: If animation not found or user not authorized
    """
    # Query the animation
    result = await db.execute(
        select(Animation)
        .where(Animation.id == animation_id)
        .where(Animation.user_id == user_id)
    )
    animation = result.scalars().first()
    
    if not animation:
        return None
    
    # Create and return the status response
    return AnimationStatusResponse(
        id=animation.id,
        status=animation.status,
        progress=animation.progress,
        status_message=animation.status_message,
        video_url=animation.video_url if animation.status == "completed" else None,
        created_at=animation.created_at
    )


async def update_animation_status(
    db: AsyncSession,
    animation_id: UUID,
    status: str,
    progress: float,
    status_message: Optional[str] = None
) -> bool:
    """
    Update the status of an animation.
    
    Args:
        db: Database session
        animation_id: ID of the animation to update
        status: New status value
        progress: Progress percentage (0-100)
        status_message: Optional status message
        
    Returns:
        bool: True if update successful, False otherwise
    """
    # Query the animation
    result = await db.execute(
        select(Animation).where(Animation.id == animation_id)
    )
    animation = result.scalars().first()
    
    if not animation:
        return False
    
    # Update the status information
    animation.status = status
    animation.progress = progress
    animation.status_message = status_message
    
    # Commit changes
    await db.commit()
    return True 