# GBLMS Backend API

FastAPI backend for the Goal-Based Learning Management System with Scout AI integration.

## Features

- **Scout AI Integration**: Intelligent roadmap generation using Google Gemini
- **Simple Authentication**: Username-based auth (password always "password")
- **Database Support**: Supabase (PostgreSQL), Neo4j (Skills Graph), Redis (Caching)
- **Mock Mode**: All databases have mock modes for development without credentials
- **Free Tier**: Designed to run entirely on free tier services

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your credentials
```

**Minimum required for basic functionality:**
```env
GOOGLE_API_KEY=your-google-api-key
FRONTEND_URL=http://localhost:5173
SECRET_KEY=your-secret-key
```

**Optional (for full functionality):**
- Supabase credentials
- Neo4j Aura credentials
- Upstash Redis URL

### 3. Run Development Server

```bash
python -src/main.py
```

Or with uvicorn:

```bash
uvicorn src.main:app --reload --port 8000
```

The API will be available at `http://localhost:8000`

- Swagger docs: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## API Endpoints

### Authentication

**POST /api/auth/login**
```json
{
  "username": "john",
  "password": "password"
}
```

Returns:
```json
{
  "access_token": "eyJ...",
  "token_type": "bearer",
  "username": "john"
}
```

### Roadmap Generation

**POST /api/roadmaps/generate**
```json
{
  "career_goal": "Full Stack Developer",
  "current_skills": [
    {
      "skill": "JavaScript",
      "score": 7,
      "level": "intermediate"
    }
  ],
  "learning_preferences": {
    "learning_style": "hands-on",
    "time_commitment_hours_per_week": 15
  }
}
```

**GET /api/roadmaps/{roadmap_id}**

Returns full roadmap with modules, resources, and projects.

**PUT /api/roadmaps/{roadmap_id}**
```json
{
  "user_prompt": "Add more React projects",
  "existing_roadmap": { ... }
}
```

**GET /api/roadmaps/user/{username}**

Returns all roadmaps for a user.

## Mock Mode

When database credentials are not configured, the backend automatically runs in mock mode:

- **Supabase Mock**: In-memory user and roadmap storage
- **Neo4j Mock**: Predefined skill relationships
- **Redis Mock**: In-memory cache with dict

This allows you to develop and test without setting up databases.

## Database Setup

### Supabase (PostgreSQL)

1. Create a free account at [supabase.com](https://supabase.com)
2. Create a new project
3. Run the SQL schema:

```sql
-- Users table
CREATE TABLE users (
  username TEXT PRIMARY KEY,
  created_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP
);

-- Roadmaps table
CREATE TABLE roadmaps (
  id TEXT PRIMARY KEY,
  user_id TEXT REFERENCES users(username),
  title TEXT,
  career_goal TEXT,
  estimated_weeks INTEGER,
  modules JSONB,
  current_module INTEGER DEFAULT 0,
  progress_percentage REAL DEFAULT 0.0,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- Index for user lookups
CREATE INDEX idx_roadmaps_user_id ON roadmaps(user_id);
```

### Neo4j Aura (Skills Graph)

1. Create a free account at [neo4j.com/aura](https://neo4j.com/cloud/aura/)
2. Create a new AuraDB Free instance
3. Import LinkedIn Skills dataset (instructions in `/database/neo4j/README.md`)

### Upstash Redis (Cache)

1. Create a free account at [upstash.com](https://upstash.com)
2. Create a new Redis database
3. Copy the Redis URL to `.env`

## Deployment to Render

### Option 1: Using render.yaml (Recommended)

1. Push code to GitHub
2. Connect repository to Render
3. Render will auto-detect `render.yaml`
4. Add environment variables in Render dashboard
5. Deploy

### Option 2: Manual Setup

1. Create new Web Service on Render
2. Connect your repository
3. Configure:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
   - **Environment**: Python 3.11
4. Add environment variables
5. Deploy

### Required Environment Variables on Render

```
GOOGLE_API_KEY=your-key
FRONTEND_URL=https://your-app.vercel.app
SECRET_KEY=random-secret-key
SUPABASE_URL=your-url
SUPABASE_KEY=your-key
NEO4J_URI=your-uri
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your-password
REDIS_URL=your-redis-url
```

## Project Structure

```
backend/
├── src/
│   ├── api/
│   │   ├── auth_routes.py      # Authentication endpoints
│   │   └── roadmap_routes.py   # Roadmap CRUD endpoints
│   ├── db/
│   │   ├── supabase_client.py  # PostgreSQL client
│   │   ├── neo4j_client.py     # Skills graph client
│   │   └── redis_client.py     # Cache client
│   ├── services/
│   │   ├── auth.py             # Auth utilities (JWT, password)
│   │   └── scout_client.py     # Scout AI integration
│   ├── models/
│   │   └── schemas.py          # Pydantic models
│   └── main.py                 # FastAPI application
├── requirements.txt            # Python dependencies
├── Dockerfile                  # Docker configuration
├── render.yaml                 # Render deployment config
└── .env.example                # Environment template
```

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black src/
```

### Type Checking

```bash
mypy src/
```

## Architecture

- **FastAPI**: Modern Python web framework
- **Google Gemini**: AI for roadmap generation
- **Supabase**: User and roadmap persistence
- **Neo4j**: Skills graph and relationships
- **Redis**: Caching layer for performance

## License

MIT
