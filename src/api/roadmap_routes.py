from fastapi import APIRouter, HTTPException, status, Header
from typing import Optional, List
from ..models.schemas import (
    RoadmapGenerateRequest,
    RoadmapUpdateRequest,
    RoadmapResponse,
    Roadmap
)
from ..services.scout_client import scout_client
from ..db.supabase_mcp_client import supabase_mcp_client as supabase_client
from ..db.redis_client import redis_client
from ..services.auth import decode_access_token

router = APIRouter(prefix="/api/roadmaps", tags=["roadmaps"])

def get_username_from_token(authorization: Optional[str] = Header(None)) -> str:
    """Extract username from JWT token."""
    if not authorization or not authorization.startswith("Bearer "):
        return "anonymous"

    token = authorization.replace("Bearer ", "")
    payload = decode_access_token(token)
    return payload.get("sub", "anonymous") if payload else "anonymous"

@router.post("/generate", response_model=RoadmapResponse)
async def generate_roadmap(
    request: RoadmapGenerateRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Generate a new personalized learning roadmap.
    Uses Scout AI to create a structured learning path based on:
    - Career goal
    - Current skills
    - Learning preferences
    """
    try:
        # Get username from token
        username = get_username_from_token(authorization)

        # Convert Pydantic models to dicts
        skills_dict = [skill.dict() for skill in request.current_skills]
        preferences_dict = request.learning_preferences.dict() if request.learning_preferences else None

        # Generate roadmap using Scout
        result = await scout_client.generate_roadmap(
            career_goal=request.career_goal,
            current_skills=skills_dict,
            learning_preferences=preferences_dict,
            user_id=username
        )

        # Save to database
        roadmap_data = result["roadmap"]
        await supabase_client.save_roadmap(roadmap_data)

        # Cache in Redis for faster retrieval
        cache_key = f"roadmap:{roadmap_data['id']}"
        redis_client.set(cache_key, roadmap_data, expire_seconds=3600)

        return result

    except Exception as e:
        print(f"Error generating roadmap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate roadmap: {str(e)}"
        )

@router.get("/{roadmap_id}", response_model=dict)
async def get_roadmap(roadmap_id: str):
    """
    Get a specific roadmap by ID.
    Checks Redis cache first, then falls back to database.
    """
    try:
        # Check cache first
        cache_key = f"roadmap:{roadmap_id}"
        cached_roadmap = redis_client.get(cache_key)
        if cached_roadmap:
            return {"roadmap": cached_roadmap}

        # Fallback to database
        roadmap = await supabase_client.get_roadmap(roadmap_id)
        if not roadmap:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Roadmap {roadmap_id} not found"
            )

        # Cache for next time
        redis_client.set(cache_key, roadmap, expire_seconds=3600)

        return {"roadmap": roadmap}

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error retrieving roadmap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve roadmap: {str(e)}"
        )

@router.put("/{roadmap_id}", response_model=RoadmapResponse)
async def update_roadmap(
    roadmap_id: str,
    request: RoadmapUpdateRequest,
    authorization: Optional[str] = Header(None)
):
    """
    Update an existing roadmap based on user feedback.
    Scout AI will modify the roadmap according to the user's request.
    """
    try:
        # Get existing roadmap
        existing = await supabase_client.get_roadmap(roadmap_id)
        if not existing:
            # Use provided roadmap if database doesn't have it
            if not request.existing_roadmap:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Roadmap {roadmap_id} not found"
                )
            existing = request.existing_roadmap.dict()

        # Update using Scout
        result = await scout_client.update_roadmap(
            roadmap_id=roadmap_id,
            user_prompt=request.user_prompt,
            existing_roadmap=existing
        )

        # Save updated roadmap
        updated_roadmap = result["roadmap"]
        await supabase_client.update_roadmap(roadmap_id, updated_roadmap)

        # Update cache
        cache_key = f"roadmap:{roadmap_id}"
        redis_client.set(cache_key, updated_roadmap, expire_seconds=3600)

        return result

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error updating roadmap: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update roadmap: {str(e)}"
        )

@router.get("/user/{username}", response_model=dict)
async def get_user_roadmaps(username: str):
    """Get all roadmaps for a specific user."""
    try:
        roadmaps = await supabase_client.get_user_roadmaps(username)
        return {"roadmaps": roadmaps, "count": len(roadmaps)}

    except Exception as e:
        print(f"Error retrieving user roadmaps: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve roadmaps: {str(e)}"
        )
