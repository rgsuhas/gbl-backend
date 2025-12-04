from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from ..models.schemas import UserLogin, Token, User
from ..services.auth import simple_auth_login, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from ..db.supabase_mcp_client import supabase_mcp_client as supabase_client

router = APIRouter(prefix="/api/auth", tags=["authentication"])

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """
    Simple login endpoint.
    Password is always "password" for any username.
    Creates user if doesn't exist.
    """
    # Validate credentials (password must be "password")
    if not simple_auth_login(credentials.username, credentials.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Get or create user
    user = await supabase_client.get_user(credentials.username)
    if not user:
        user = await supabase_client.create_user(credentials.username)
    else:
        await supabase_client.update_last_login(credentials.username)

    # Create access token
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": credentials.username},
        expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": credentials.username
    }

@router.get("/me", response_model=User)
async def get_current_user(username: str):
    """Get current user information."""
    user = await supabase_client.get_user(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user
