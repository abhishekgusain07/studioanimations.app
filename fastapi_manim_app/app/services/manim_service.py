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
from app.services.conversation_service import get_or_create_conversation, save_animation

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
        # If we have a database session, get or create the conversation
        conversation = None
        if db and user_id:
            conversation = await get_or_create_conversation(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id
            )
            conversation_id = conversation.id
        
        # Generate Manim code from the query
        manim_code = await generate_manim_code_from_llm(query, previous_code)
        
        # Save the code to a file
        script_path = job_dir / "generatedmanimscene_script.py"
        with open(script_path, "w") as f:
            f.write(manim_code)
        
        # Run Manim to generate the animation with the specified quality
        success, error_msg = await run_manim_script(script_path, media_dir, quality)
        
        if not success:
            # If we have a database session, save the failed animation
            if db and conversation_id and user_id:
                animation = await save_animation(
                    db=db,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    query=query,
                    generated_code=manim_code,
                    video_url="",
                    quality=quality,
                    success=False,
                    error_message=error_msg
                )
                animation_id = animation.id
            
            return False, "", error_msg, animation_id, conversation_id
        
        # Find the generated video file
        video_file = None
        for file in (media_dir / "videos" / "generatedmanimscene_script" / "480p15").glob("GeneratedManimScene.mp4"):
            video_file = file
            break
        
        # In case the exact path pattern doesn't match, try a broader search
        if video_file is None:
            for file in media_dir.rglob("GeneratedManimScene.mp4"):
                video_file = file
                break
        
        if video_file is None:
            error_msg = "Generated video file not found"
            # If we have a database session, save the failed animation
            if db and conversation_id and user_id:
                animation = await save_animation(
                    db=db,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    query=query,
                    generated_code=manim_code,
                    video_url="",
                    quality=quality,
                    success=False,
                    error_message=error_msg
                )
                animation_id = animation.id
            
            return False, "", error_msg, animation_id, conversation_id
        
        # Copy the video to the public directory with a unique name
        output_filename = f"{job_id}_GeneratedManimScene.mp4"
        output_path = settings.STATIC_VIDEOS_DIR / output_filename
        shutil.copy2(video_file, output_path)
        
        # Construct the URL for the video
        video_url = f"{settings.SERVED_VIDEOS_PATH_PREFIX}/{output_filename}"
        
        # If we have a database session, save the successful animation
        if db and conversation_id and user_id:
            animation = await save_animation(
                db=db,
                conversation_id=conversation_id,
                user_id=user_id,
                query=query,
                generated_code=manim_code,
                video_url=video_url,
                quality=quality,
                success=True
            )
            animation_id = animation.id
        
        # Clean up temporary files
        shutil.rmtree(media_dir, ignore_errors=True)
        script_path.unlink(missing_ok=True)
        
        # Try to remove the job directory if it's empty
        try:
            job_dir.rmdir()
        except OSError:
            # Directory not empty, that's ok
            pass
        
        return True, video_url, "", animation_id, conversation_id
        
    except Exception as e:
        logger.exception("Error generating animation", error=str(e))
        # Clean up in case of error
        shutil.rmtree(job_dir, ignore_errors=True)
        
        # If we have a database session, save the failed animation
        if db and conversation_id and user_id:
            try:
                animation = await save_animation(
                    db=db,
                    conversation_id=conversation_id,
                    user_id=user_id,
                    query=query,
                    generated_code=previous_code or "",
                    video_url="",
                    quality=quality,
                    success=False,
                    error_message=str(e)
                )
                animation_id = animation.id
            except Exception as db_error:
                logger.exception("Error saving failed animation to database", error=str(db_error))
        
        return False, "", f"Error generating animation: {str(e)}", animation_id, conversation_id 