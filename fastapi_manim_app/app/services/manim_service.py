"""
Service for generating Manim animations based on user queries.
"""
import asyncio
import shutil
import uuid
from pathlib import Path
from typing import Tuple, Dict, Optional
from uuid import UUID

import structlog
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.animation import QualityOption
from app.models.db_models import MessageType, AnimationStatus, Animation
from app.services.conversation_service import get_or_create_conversation, save_animation
from app.services.message_service import create_message
from app.services.animation_service import update_animation_status

logger = structlog.get_logger(__name__)

# Mapping of quality options to Manim quality flags
QUALITY_FLAG_MAP: Dict[str, str] = {
    QualityOption.LOW: "-ql",     # Low quality, faster rendering
    QualityOption.MEDIUM: "-qm",  # Medium quality
    QualityOption.HIGH: "-qh"     # High quality, slower rendering
}


async def generate_manim_code_from_llm(query: str, previous_code: Optional[str] = None) -> str:
    """
    Simulate generating Manim code from a Large Language Model.
    
    In a production application, this would call an external LLM API.
    
    Args:
        query: User's natural language query describing the desired animation
        previous_code: Optional previous code to use as context for improvements
        
    Returns:
        str: Python code for a Manim scene
    """
    # This is a simplified example - in production, this would call an external LLM API
    logger.info("Generating Manim code from query", 
                query=query, 
                has_previous_code=previous_code is not None)
    
    # If previous code is provided, use it as a base (in a real app, we'd send to an LLM)
    if previous_code:
        # This is a simplified example - we're just returning the previous code
        # In a real application, we would use the previous code as context for an LLM
        # to generate improved code based on the new query
        return previous_code
    
    # For now, return a simple example scene based on the query
    if "triangle" in query.lower() and "square" in query.lower():
        return """
from manim import *

class GeneratedManimScene(Scene):
    def construct(self):
        # Create a triangle
        triangle = Triangle().scale(2)
        
        # Add the triangle to the scene
        self.play(Create(triangle))
        self.wait(1)
        
        # Morph the triangle into a square
        square = Square().scale(2)
        self.play(Transform(triangle, square))
        self.wait(1)
        
        # Add a text label
        text = Text("Triangle to Square Transformation")
        text.to_edge(UP)
        self.play(Write(text))
        self.wait(1)
        """
    else:
        # Default animation if query doesn't match specific patterns
        return """
from manim import *

class GeneratedManimScene(Scene):
    def construct(self):
        # Create a circle
        circle = Circle().scale(2)
        circle.set_fill(BLUE, opacity=0.5)
        
        # Add the circle to the scene
        self.play(Create(circle))
        
        # Add a text label
        text = Text("Generated Animation")
        text.to_edge(UP)
        self.play(Write(text))
        
        # Animate the circle
        self.play(circle.animate.shift(LEFT * 2))
        self.play(circle.animate.shift(RIGHT * 4))
        self.play(circle.animate.shift(LEFT * 2))
        
        # Fade out
        self.play(FadeOut(circle), FadeOut(text))
        """


async def run_manim_script(script_path: Path, media_dir: Path, quality: QualityOption = QualityOption.LOW) -> Tuple[bool, str]:
    """
    Execute the Manim script to generate an animation.
    
    Args:
        script_path: Path to the Python script containing Manim code
        media_dir: Directory where Manim should output its media files
        quality: Quality level for the animation rendering
        
    Returns:
        Tuple[bool, str]: Success status and error message if any
    """
    logger.info("Running Manim script", script_path=str(script_path), media_dir=str(media_dir), quality=quality)
    
    # Get the appropriate quality flag based on the requested quality
    quality_flag = QUALITY_FLAG_MAP.get(quality, "-ql")  # Default to low quality if unknown
    
    # Build the Manim command
    cmd = [
        "python", "-m", "manim",
        str(script_path),
        "GeneratedManimScene",
        quality_flag,
        "--format", "mp4",
        "--media_dir", str(media_dir)
    ]
    
    # Run the command as a subprocess
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    # Wait for the process to complete and capture output
    stdout, stderr = await process.communicate()
    
    # Check if the process was successful
    if process.returncode != 0:
        error_msg = f"Manim execution failed: {stderr.decode()}"
        logger.error(
            "Manim execution failed",
            return_code=process.returncode,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )
        return False, error_msg
    
    logger.info(
        "Manim execution completed successfully",
        stdout=stdout.decode()
    )
    return True, ""


async def generate_animation_from_query(
    query: str, 
    quality: QualityOption = QualityOption.LOW,
    conversation_id: Optional[UUID] = None,
    user_id: UUID = None,
    previous_code: Optional[str] = None,
    db: Optional[AsyncSession] = None
) -> Tuple[bool, str, str, Optional[UUID], Optional[UUID]]:
    """
    Generate a Manim animation based on a user query.
    
    Args:
        query: User's natural language query
        quality: Quality level for the animation rendering
        conversation_id: Optional ID of the conversation this animation belongs to
        user_id: ID of the user requesting the animation
        previous_code: Optional previous code to use as context
        db: Optional database session for saving animation data
        
    Returns:
        Tuple[bool, str, str, UUID, UUID]: 
            - Success status
            - Video URL (if successful)
            - Error message (if failed)
            - Animation ID
            - Conversation ID
    """
    # Generate a unique job ID
    job_id = str(uuid.uuid4())
    animation_id = None
    
    # Create directories for this job
    job_dir = settings.TEMP_BASE_DIR / job_id
    media_dir = job_dir / "media_output"
    
    job_dir.mkdir(exist_ok=True)
    media_dir.mkdir(exist_ok=True)
    
    try:
        # Get or create a conversation if a database session is provided
        if db and user_id:
            conversation = await get_or_create_conversation(db, conversation_id, user_id)
            conversation_id = conversation.id
            
            # Save the user message
            await create_message(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
                content=query,
                message_type=MessageType.USER
            )
        
        # Create animation record with initial status
        if db and user_id and conversation_id:
            # Save the animation with initial status
            animation = await save_animation(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
                query=query,
                generated_code="", # Will be updated later
                video_url="",      # Will be updated later
                quality=quality,
                success=False,     # Will be updated later
                error_message=None,
                status=AnimationStatus.PENDING,
                progress=0.0,
                status_message="Initializing animation generation"
            )
            animation_id = animation.id
            await db.flush()
        
        # Update status to PROCESSING with initial progress
        if db and animation_id:
            await update_animation_status(
                db=db,
                animation_id=animation_id,
                status=AnimationStatus.PROCESSING,
                progress=10.0,
                status_message="Generating Manim code"
            )
        
        # Generate Manim code from the query
        generated_code = await generate_manim_code_from_llm(query, previous_code)
        
        # Update status with progress
        if db and animation_id:
            await update_animation_status(
                db=db,
                animation_id=animation_id,
                status=AnimationStatus.PROCESSING,
                progress=30.0,
                status_message="Code generated, preparing to render animation"
            )
        
        # Write the generated code to a file
        script_path = job_dir / "generated_manim_scene.py"
        with open(script_path, "w") as f:
            f.write(generated_code)
        
        # Update status before running Manim
        if db and animation_id:
            await update_animation_status(
                db=db,
                animation_id=animation_id,
                status=AnimationStatus.PROCESSING,
                progress=40.0,
                status_message="Starting animation rendering"
            )
        
        # Run the Manim script to generate the animation
        success, error_msg = await run_manim_script(script_path, media_dir, quality)
        
        if not success:
            # Update status to FAILED
            if db and animation_id:
                await update_animation_status(
                    db=db,
                    animation_id=animation_id,
                    status=AnimationStatus.FAILED,
                    progress=0.0,
                    status_message=f"Animation generation failed: {error_msg}"
                )
            
            if db and user_id and conversation_id:
                # Save error message as AI response if generation failed
                await create_message(
                    db=db,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    content=f"Failed to generate animation: {error_msg}",
                    message_type=MessageType.AI
                )
            return False, "", error_msg, animation_id, conversation_id
        
        # Update status after rendering is complete
        if db and animation_id:
            await update_animation_status(
                db=db,
                animation_id=animation_id,
                status=AnimationStatus.PROCESSING,
                progress=80.0,
                status_message="Rendering complete, processing video"
            )
        
        # Find the generated media file
        video_dir = media_dir / "videos" / "GeneratedManimScene"
        video_files = list(video_dir.glob("*.mp4"))
        
        if not video_files:
            error_msg = "No video output was generated"
            
            # Update status to FAILED
            if db and animation_id:
                await update_animation_status(
                    db=db,
                    animation_id=animation_id,
                    status=AnimationStatus.FAILED,
                    progress=0.0,
                    status_message=error_msg
                )
                
            if db and user_id and conversation_id:
                # Save error message as AI response
                await create_message(
                    db=db,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    content=f"Failed to generate animation: {error_msg}",
                    message_type=MessageType.AI
                )
            return False, "", error_msg, animation_id, conversation_id
        
        # Get the first video file (should only be one)
        video_path = video_files[0]
        
        # Copy to static directory with job ID in the filename
        static_dir = settings.STATIC_DIR / "manim_videos"
        static_dir.mkdir(exist_ok=True)
        
        # Use the job ID in the target filename for uniqueness
        target_name = f"{job_id}_GeneratedManimScene.mp4"
        target_path = static_dir / target_name
        shutil.copy2(video_path, target_path)
        
        # URL path to access the video
        video_url = f"/manim_videos/{target_name}"
        
        # Update the animation record with success status
        if db and animation_id:
            # Update the animation record with complete status
            await update_animation_status(
                db=db,
                animation_id=animation_id,
                status=AnimationStatus.COMPLETED,
                progress=100.0,
                status_message="Animation generated successfully"
            )
            
            # Update the animation record with generated code and video URL
            animation = await db.get(Animation, animation_id)
            if animation:
                animation.generated_code = generated_code
                animation.video_url = str(video_url)
                animation.success = True
                await db.flush()
            
            # Save AI response with animation ID
            await create_message(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
                content="Animation generated successfully",
                message_type=MessageType.AI,
                animation_id=animation_id
            )
        
        return True, video_url, "", animation_id, conversation_id
    
    except Exception as e:
        logger.exception("Error generating animation", error=str(e))
        
        if db and user_id and conversation_id:
            # Save error message as AI response
            await create_message(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
                content=f"Error generating animation: {str(e)}",
                message_type=MessageType.AI
            )
            
        return False, "", f"Error generating animation: {str(e)}", None, conversation_id
    
    finally:
        # Clean up temporary files (keep the static video file)
        if settings.CLEANUP_TEMP_FILES and job_dir.exists():
            try:
                shutil.rmtree(job_dir)
            except Exception as e:
                logger.warning("Failed to clean up temporary files", error=str(e)) 