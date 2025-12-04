# Supabase MCP Integration Setup

This guide explains how to set up and use the Supabase MCP (Model Context Protocol) server integration.

## What is Supabase MCP?

The Supabase MCP server provides an HTTP-based interface to your Supabase database, allowing the backend to interact with Supabase through MCP tools instead of the Python SDK.

**Benefits:**
- ✅ Better integration with Claude's MCP ecosystem
- ✅ Automatic error handling and retries
- ✅ Consistent interface across different database operations
- ✅ Falls back to mock mode gracefully if unavailable

## Current Status

✅ **Supabase MCP client is integrated and active**

The backend is currently using the Supabase MCP client (`supabase_mcp_client.py`). You can see this in:
- `src/api/auth_routes.py` - imports `supabase_mcp_client`
- `src/api/roadmap_routes.py` - imports `supabase_mcp_client`

## Configuration

### Step 1: Add Supabase MCP Server

You've already completed this step! The MCP server configuration is in `/.mcp.json`:

```json
{
  "mcpServers": {
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=vmbidtlbowelafgkbckq"
    }
  }
}
```

### Step 2: Add Supabase Credentials

The MCP server requires your Supabase credentials for authentication. Add these to your `.env` file:

```env
# Supabase Configuration (Required for MCP)
SUPABASE_URL=https://vmbidtlbowelafgkbckq.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

**To get your credentials:**

1. Go to your Supabase project dashboard
2. Click **Settings** → **API**
3. Copy:
   - **Project URL**: `https://vmbidtlbowelafgkbckq.supabase.co`
   - **anon/public key**: `eyJhbG...` (long string)
4. Add to `.env`

### Step 3: Restart Backend

```bash
# Backend will automatically detect and use MCP
python -m uvicorn src.main:app --reload --port 8000
```

You should see:
```
✓ Supabase MCP client initialized with URL: https://mcp.supabase.com/mcp?project_ref=vmbidtlbowelafgkbckq
✓ Using Supabase credentials for MCP authentication
```

## How It Works

### 1. Initialization

When the backend starts:
1. Reads `.mcp.json` to get MCP server URL
2. Checks for `SUPABASE_URL` and `SUPABASE_KEY` in environment
3. If both are present, enables MCP mode
4. If not, falls back to mock mode (in-memory storage)

### 2. Database Operations

The MCP client provides these operations:
- `create_user(username)` - Create a new user
- `get_user(username)` - Retrieve user by username
- `update_last_login(username)` - Update login timestamp
- `save_roadmap(roadmap_data)` - Save a roadmap
- `get_roadmap(roadmap_id)` - Retrieve a roadmap
- `update_roadmap(roadmap_id, data)` - Update a roadmap
- `get_user_roadmaps(username)` - Get all roadmaps for a user

### 3. MCP Communication

Each operation:
1. Constructs a JSON-RPC request
2. Adds Supabase authentication headers
3. POSTs to the MCP server URL
4. Parses and returns the response
5. Falls back to mock data on error

### 4. Mock Mode Fallback

If MCP is unavailable (no credentials, server down, etc.):
- All operations continue to work
- Data is stored in-memory (lost on restart)
- Perfect for development and testing

## Testing

### Test MCP Client

```bash
cd backend

# Test import
python -c "from src.db.supabase_mcp_client import supabase_mcp_client; print('✓ MCP client loaded')"

# Test user creation (requires credentials in .env)
python -c "from src.db.supabase_mcp_client import supabase_mcp_client; import asyncio; print(asyncio.run(supabase_mcp_client.create_user('testuser')))"
```

### Test via API

```bash
# Login (creates user via MCP)
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username": "mcp_test_user", "password": "password"}'

# Should return JWT token
```

### Check Backend Logs

Look for these messages in the backend logs:

**MCP Enabled:**
```
✓ Supabase MCP client initialized with URL: https://mcp.supabase.com/mcp?project_ref=vmbidtlbowelafgkbckq
✓ Using Supabase credentials for MCP authentication
```

**MCP Not Configured:**
```
⚠ Supabase MCP URL found but SUPABASE_URL/KEY not set
  Add these to .env to enable MCP mode:
  SUPABASE_URL=your-project-url
  SUPABASE_KEY=your-anon-key
Warning: Supabase MCP not fully configured. Using mock mode.
```

## Troubleshooting

### Issue: "401 Unauthorized" errors in logs

**Cause**: Supabase credentials not set or incorrect

**Fix**:
1. Add `SUPABASE_URL` and `SUPABASE_KEY` to `.env`
2. Verify credentials are correct in Supabase dashboard
3. Restart backend

### Issue: "MCP not fully configured"

**Cause**: Missing `.mcp.json` or missing credentials

**Fix**:
1. Verify `.mcp.json` exists in `backend/` directory
2. Add Supabase credentials to `.env`
3. Restart backend

### Issue: Operations work but data isn't persisted

**Cause**: Running in mock mode (no database connection)

**Fix**:
1. Set up Supabase database using `/database/supabase/schema.sql`
2. Add credentials to `.env`
3. Restart backend

### Issue: Want to switch back to direct Python SDK

**Fix**:
Edit `src/api/auth_routes.py` and `src/api/roadmap_routes.py`:

```python
# Change this:
from ..db.supabase_mcp_client import supabase_mcp_client as supabase_client

# To this:
from ..db.supabase_client import supabase_client
```

## MCP vs Direct SDK

| Feature | MCP Client | Direct SDK |
|---------|------------|------------|
| **Setup** | Requires `.mcp.json` + credentials | Requires credentials only |
| **Interface** | HTTP/JSON-RPC | Python SDK |
| **Fallback** | Mock mode | Mock mode |
| **Performance** | HTTP overhead | Direct connection |
| **Integration** | Claude MCP ecosystem | Standalone |
| **Recommended** | ✅ Yes (for Claude Code) | For non-MCP environments |

## Production Deployment

### Render

Add environment variables in Render dashboard:

```env
SUPABASE_URL=https://vmbidtlbowelafgkbckq.supabase.co
SUPABASE_KEY=your-supabase-anon-key
```

The `.mcp.json` file will be deployed with your code automatically.

### Vercel/Other Platforms

Same approach - add environment variables to your hosting platform.

## Next Steps

1. ✅ MCP client integrated
2. 🔲 Add Supabase credentials to `.env`
3. 🔲 Set up database tables (see `/database/supabase/schema.sql`)
4. 🔲 Test user creation and roadmap saving
5. 🔲 Deploy to production with credentials

## Resources

- [Supabase MCP Documentation](https://supabase.com/docs/guides/ai/mcp)
- [Model Context Protocol Spec](https://spec.modelcontextprotocol.io/)
- [Backend Database Clients README](src/db/README.md)
