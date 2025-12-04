from supabase import create_client, Client
import os
from typing import Optional, Dict, Any, List
from datetime import datetime

class SupabaseClient:
    def __init__(self):
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")

        if not url or not key:
            print("Warning: Supabase credentials not configured. Using mock mode.")
            self.client: Optional[Client] = None
            self.mock_mode = True
        else:
            self.client: Client = create_client(url, key)
            self.mock_mode = False

    async def create_user(self, username: str) -> Dict[str, Any]:
        """Create a new user."""
        if self.mock_mode:
            return {
                "username": username,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat()
            }

        data = {
            "username": username,
            "created_at": datetime.utcnow().isoformat(),
            "last_login": datetime.utcnow().isoformat()
        }
        result = self.client.table("users").insert(data).execute()
        return result.data[0] if result.data else data

    async def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        if self.mock_mode:
            return {
                "username": username,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat()
            }

        result = self.client.table("users").select("*").eq("username", username).execute()
        return result.data[0] if result.data else None

    async def update_last_login(self, username: str) -> None:
        """Update user's last login timestamp."""
        if self.mock_mode:
            return

        self.client.table("users").update({
            "last_login": datetime.utcnow().isoformat()
        }).eq("username", username).execute()

    async def save_roadmap(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a roadmap to the database."""
        if self.mock_mode:
            return roadmap_data

        result = self.client.table("roadmaps").insert(roadmap_data).execute()
        return result.data[0] if result.data else roadmap_data

    async def get_roadmap(self, roadmap_id: str) -> Optional[Dict[str, Any]]:
        """Get a roadmap by ID."""
        if self.mock_mode:
            return None

        result = self.client.table("roadmaps").select("*").eq("id", roadmap_id).execute()
        return result.data[0] if result.data else None

    async def update_roadmap(self, roadmap_id: str, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a roadmap."""
        if self.mock_mode:
            return roadmap_data

        result = self.client.table("roadmaps").update(roadmap_data).eq("id", roadmap_id).execute()
        return result.data[0] if result.data else roadmap_data

    async def get_user_roadmaps(self, username: str) -> List[Dict[str, Any]]:
        """Get all roadmaps for a user."""
        if self.mock_mode:
            return []

        result = self.client.table("roadmaps").select("*").eq("user_id", username).execute()
        return result.data if result.data else []

# Global instance
supabase_client = SupabaseClient()
