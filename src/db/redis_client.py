import redis
import json
import os
from typing import Optional, Any

class RedisClient:
    def __init__(self):
        redis_url = os.getenv("REDIS_URL")

        if not redis_url:
            print("Warning: Redis URL not configured. Using mock mode.")
            self.client = None
            self.mock_mode = True
            self.mock_cache = {}
        else:
            self.client = redis.from_url(redis_url, decode_responses=True)
            self.mock_mode = False

    def set(self, key: str, value: Any, expire_seconds: int = 3600) -> bool:
        """Set a key-value pair with expiration."""
        if self.mock_mode:
            self.mock_cache[key] = json.dumps(value)
            return True

        try:
            self.client.setex(key, expire_seconds, json.dumps(value))
            return True
        except Exception as e:
            print(f"Redis set error: {e}")
            return False

    def get(self, key: str) -> Optional[Any]:
        """Get a value by key."""
        if self.mock_mode:
            value = self.mock_cache.get(key)
            return json.loads(value) if value else None

        try:
            value = self.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            print(f"Redis get error: {e}")
            return None

    def delete(self, key: str) -> bool:
        """Delete a key."""
        if self.mock_mode:
            if key in self.mock_cache:
                del self.mock_cache[key]
                return True
            return False

        try:
            self.client.delete(key)
            return True
        except Exception as e:
            print(f"Redis delete error: {e}")
            return False

    def exists(self, key: str) -> bool:
        """Check if a key exists."""
        if self.mock_mode:
            return key in self.mock_cache

        try:
            return bool(self.client.exists(key))
        except Exception as e:
            print(f"Redis exists error: {e}")
            return False

# Global instance
redis_client = RedisClient()
