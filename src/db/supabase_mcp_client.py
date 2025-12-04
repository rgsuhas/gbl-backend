import httpx
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import json

class SupabaseMCPClient:
    """
    Supabase client that uses the Supabase MCP server for database operations.
    This provides an HTTP-based interface to Supabase instead of the Python SDK.
    """

    def __init__(self):
        # Read MCP config
        mcp_config_path = os.path.join(os.path.dirname(__file__), "../../.mcp.json")
        self.mcp_url = None
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        self.mock_mode = True

        try:
            if os.path.exists(mcp_config_path):
                with open(mcp_config_path, 'r') as f:
                    config = json.load(f)
                    if 'mcpServers' in config and 'supabase' in config['mcpServers']:
                        self.mcp_url = config['mcpServers']['supabase']['url']

                        # Only enable MCP mode if we have Supabase credentials for auth
                        if self.supabase_url and self.supabase_key:
                            self.mock_mode = False
                            print(f"✓ Supabase MCP client initialized with URL: {self.mcp_url}")
                            print(f"✓ Using Supabase credentials for MCP authentication")
                        else:
                            print(f"⚠ Supabase MCP URL found but SUPABASE_URL/KEY not set")
                            print(f"  Add these to .env to enable MCP mode:")
                            print(f"  SUPABASE_URL=your-project-url")
                            print(f"  SUPABASE_KEY=your-anon-key")

            if self.mock_mode:
                print("Warning: Supabase MCP not fully configured. Using mock mode.")
                self.mock_data = {
                    'users': {},
                    'roadmaps': {}
                }
        except Exception as e:
            print(f"Warning: Failed to load Supabase MCP config: {e}. Using mock mode.")
            self.mock_mode = True
            self.mock_data = {
                'users': {},
                'roadmaps': {}
            }

    async def _call_mcp(self, tool: str, arguments: Dict[str, Any]) -> Any:
        """Call the Supabase MCP server with a tool and arguments."""
        if self.mock_mode:
            return None

        # Add Supabase authentication headers
        headers = {
            'Content-Type': 'application/json',
            'apikey': self.supabase_key,
            'Authorization': f'Bearer {self.supabase_key}'
        }

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                self.mcp_url,
                headers=headers,
                json={
                    "jsonrpc": "2.0",
                    "method": "tools/call",
                    "params": {
                        "name": tool,
                        "arguments": arguments
                    },
                    "id": 1
                }
            )
            response.raise_for_status()
            result = response.json()

            if 'error' in result:
                raise Exception(f"MCP Error: {result['error']}")

            return result.get('result', {})

    async def create_user(self, username: str) -> Dict[str, Any]:
        """Create a new user."""
        if self.mock_mode:
            user_data = {
                "username": username,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat()
            }
            self.mock_data['users'][username] = user_data
            return user_data

        try:
            # Use MCP to insert into users table
            result = await self._call_mcp('supabase_insert', {
                'table': 'users',
                'data': {
                    'username': username,
                    'created_at': datetime.utcnow().isoformat(),
                    'last_login': datetime.utcnow().isoformat()
                }
            })
            return result.get('data', [{}])[0] if result else {}
        except Exception as e:
            print(f"MCP create_user error: {e}")
            # Fallback to mock
            return {
                "username": username,
                "created_at": datetime.utcnow().isoformat(),
                "last_login": datetime.utcnow().isoformat()
            }

    async def get_user(self, username: str) -> Optional[Dict[str, Any]]:
        """Get user by username."""
        if self.mock_mode:
            return self.mock_data['users'].get(username)

        try:
            # Use MCP to select from users table
            result = await self._call_mcp('supabase_select', {
                'table': 'users',
                'filters': {'username': username},
                'limit': 1
            })
            data = result.get('data', [])
            return data[0] if data else None
        except Exception as e:
            print(f"MCP get_user error: {e}")
            return None

    async def update_last_login(self, username: str) -> None:
        """Update user's last login timestamp."""
        if self.mock_mode:
            if username in self.mock_data['users']:
                self.mock_data['users'][username]['last_login'] = datetime.utcnow().isoformat()
            return

        try:
            await self._call_mcp('supabase_update', {
                'table': 'users',
                'filters': {'username': username},
                'data': {'last_login': datetime.utcnow().isoformat()}
            })
        except Exception as e:
            print(f"MCP update_last_login error: {e}")

    async def save_roadmap(self, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Save a roadmap to the database."""
        if self.mock_mode:
            roadmap_id = roadmap_data['id']
            self.mock_data['roadmaps'][roadmap_id] = roadmap_data
            return roadmap_data

        try:
            result = await self._call_mcp('supabase_insert', {
                'table': 'roadmaps',
                'data': roadmap_data
            })
            return result.get('data', [roadmap_data])[0] if result else roadmap_data
        except Exception as e:
            print(f"MCP save_roadmap error: {e}")
            return roadmap_data

    async def get_roadmap(self, roadmap_id: str) -> Optional[Dict[str, Any]]:
        """Get a roadmap by ID."""
        if self.mock_mode:
            return self.mock_data['roadmaps'].get(roadmap_id)

        try:
            result = await self._call_mcp('supabase_select', {
                'table': 'roadmaps',
                'filters': {'id': roadmap_id},
                'limit': 1
            })
            data = result.get('data', [])
            return data[0] if data else None
        except Exception as e:
            print(f"MCP get_roadmap error: {e}")
            return None

    async def update_roadmap(self, roadmap_id: str, roadmap_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update a roadmap."""
        if self.mock_mode:
            self.mock_data['roadmaps'][roadmap_id] = roadmap_data
            return roadmap_data

        try:
            result = await self._call_mcp('supabase_update', {
                'table': 'roadmaps',
                'filters': {'id': roadmap_id},
                'data': roadmap_data
            })
            return result.get('data', [roadmap_data])[0] if result else roadmap_data
        except Exception as e:
            print(f"MCP update_roadmap error: {e}")
            return roadmap_data

    async def get_user_roadmaps(self, username: str) -> List[Dict[str, Any]]:
        """Get all roadmaps for a user."""
        if self.mock_mode:
            return [rm for rm in self.mock_data['roadmaps'].values()
                    if rm.get('user_id') == username]

        try:
            result = await self._call_mcp('supabase_select', {
                'table': 'roadmaps',
                'filters': {'user_id': username},
                'order': {'column': 'created_at', 'ascending': False}
            })
            return result.get('data', [])
        except Exception as e:
            print(f"MCP get_user_roadmaps error: {e}")
            return []

# Global instance
supabase_mcp_client = SupabaseMCPClient()
