"""
Routes for generating Manim animations.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from app.services.manim_service import generate_animation_from_query
from app.models.animation import QualityOption

router = APIRouter(prefix="/api", tags=["animation"])


class AnimationRequest(BaseModel):
    """Request model for animation generation."""
    query: str
    quality: QualityOption = QualityOption.LOW


class AnimationResponse(BaseModel):
    """Response model for animation generation."""
    success: bool
    video_url: str = ""
    message: str = ""


@router.post("/generate-animation", response_model=AnimationResponse)
async def generate_animation(request: AnimationRequest) -> AnimationResponse:
    """
    Generate a Manim animation based on a user query.
    
    Args:
        request: Animation request containing:
            - query: Description of the animation to generate
            - quality: Video quality setting (low, medium, high)
              Low quality is faster to render but less detailed.
              Medium quality offers a balance between speed and detail.
              High quality produces the best visual results but takes longer to render.
        
    Returns:
        AnimationResponse: Response containing success status and video URL
        
    Raises:
        HTTPException: If animation generation fails
    """
    success, video_url, error_msg = await generate_animation_from_query(
        query=request.query, 
        quality=request.quality
    )
    
    if not success:
        raise HTTPException(
            status_code=500,
            detail=error_msg or "Failed to generate animation"
        )
    
    return AnimationResponse(
        success=True,
        video_url=video_url,
        message="Animation generated successfully"
    ) 