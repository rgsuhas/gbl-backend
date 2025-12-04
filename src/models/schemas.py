from pydantic import BaseModel, Field
from typing import Optional, List, Literal
from datetime import datetime

# User Models
class User(BaseModel):
    username: str
    created_at: Optional[datetime] = None
    last_login: Optional[datetime] = None

class UserLogin(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    username: str

# Skill Models
class SkillAssessment(BaseModel):
    skill: str
    score: int = Field(ge=1, le=10)
    level: Literal['beginner', 'intermediate', 'advanced']
    last_used: Optional[str] = None

# Learning Preferences
class LearningPreferences(BaseModel):
    learning_style: Optional[Literal['visual', 'hands-on', 'reading', 'mixed']] = None
    time_commitment_hours_per_week: Optional[int] = Field(None, ge=1, le=168)
    focus_areas: Optional[List[str]] = None
    exclude_topics: Optional[List[str]] = None
    target_completion_date: Optional[str] = None

# Resource Models
ResourceType = Literal['video', 'article', 'documentation', 'interactive-lab', 'book']
DifficultyLevel = Literal['beginner', 'intermediate', 'advanced']

class LearningResource(BaseModel):
    title: str
    type: ResourceType
    url: str
    duration: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty: DifficultyLevel
    description: Optional[str] = None

class Project(BaseModel):
    title: str
    description: str
    estimated_hours: int
    skills_applied: List[str]
    deliverables: List[str]
    difficulty: DifficultyLevel

# Roadmap Models
class RoadmapModule(BaseModel):
    id: str
    title: str
    description: str
    estimated_hours: int
    skills_taught: List[str]
    resources: List[LearningResource]
    project: Optional[Project] = None
    prerequisite_skills: Optional[List[str]] = None
    learning_outcomes: Optional[List[str]] = None
    difficulty: Optional[DifficultyLevel] = None

class Roadmap(BaseModel):
    id: str
    user_id: str
    title: str
    career_goal: str
    estimated_weeks: int
    modules: List[RoadmapModule]
    current_module: Optional[int] = None
    progress_percentage: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

# Request Models
class RoadmapGenerateRequest(BaseModel):
    career_goal: str
    current_skills: List[SkillAssessment]
    learning_preferences: Optional[LearningPreferences] = None
    user_id: Optional[str] = None

class RoadmapUpdateRequest(BaseModel):
    user_prompt: str
    existing_roadmap: Optional[Roadmap] = None

# Response Models
class RoadmapResponse(BaseModel):
    roadmap: Roadmap
    message: str
    processing_time_seconds: Optional[float] = None
