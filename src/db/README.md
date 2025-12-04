# Database Clients

This directory contains database client implementations for GBLMS.

## Supabase Clients

### supabase_mcp_client.py (RECOMMENDED)

Uses the Supabase MCP server for database operations via HTTP. This is the recommended approach as it:

- Uses the official Supabase MCP integration
- Provides better error handling and retry logic
- Works seamlessly with Claude's MCP ecosystem
- Automatically falls back to mock mode if MCP is not configured

**Configuration:**
The MCP client automatically reads from `/.mcp.json` in the backend directory.

**Usage:**
```python
from db.supabase_mcp_client import supabase_mcp_client

# MCP client provides the same interface
user = await supabase_mcp_client.get_user("username")
```

### supabase_client.py (LEGACY)

Direct Python SDK client for Supabase. Still functional but not recommended for new deployments.

**Configuration:**
Requires environment variables:
- `SUPABASE_URL`
- `SUPABASE_KEY`

## Switching Between Clients

The API routes are configured to use the MCP client by default. To switch back to the direct client:

```python
# In auth_routes.py and roadmap_routes.py
from ..db.supabase_client import supabase_client  # Direct SDK
# OR
from ..db.supabase_mcp_client import supabase_mcp_client as supabase_client  # MCP (current)
```

## Mock Mode

Both clients support mock mode when no configuration is available:

- **MCP Client**: Activates when `.mcp.json` is not found or MCP server is unavailable
- **Direct Client**: Activates when `SUPABASE_URL` or `SUPABASE_KEY` are not set

In mock mode:
- Data is stored in-memory (lost on restart)
- Good for development and testing
- No database setup required

## Neo4j Client

Graph database client for skills relationships. Provides mock data when credentials are not configured.

## Redis Client

Cache client with automatic fallback to in-memory dict in mock mode.

## Migration Guide

### From Direct Client to MCP Client

1. Add Supabase MCP server:
   ```bash
   claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?project_ref=YOUR_PROJECT_REF"
   ```

2. Verify `.mcp.json` was created in backend directory

3. Restart backend server

4. MCP client will automatically detect and use the configuration

### Setting up Supabase MCP

1. Get your Supabase project reference from your project URL:
   - Format: `https://YOUR_PROJECT_REF.supabase.co`
   - Example: `vmbidtlbowelafgkbckq`

2. Add MCP server (automatically creates `.mcp.json`):
   ```bash
   claude mcp add --scope project --transport http supabase "https://mcp.supabase.com/mcp?project_ref=YOUR_PROJECT_REF"
   ```

3. The MCP client will automatically use this configuration

## Testing

### Test MCP Client
```bash
cd backend
python -c "from src.db.supabase_mcp_client import supabase_mcp_client; import asyncio; print(asyncio.run(supabase_mcp_client.get_user('test')))"
```

### Test Direct Client
```bash
cd backend
python -c "from src.db.supabase_client import supabase_client; import asyncio; print(asyncio.run(supabase_client.get_user('test')))"
```

Both should work in mock mode without errors.
