import google.generativeai as genai
import os
import json
from typing import Dict, Any, List, Optional
from datetime import datetime
import uuid

# Configure Gemini
genai.configure(api_key=os.getenv("GOOGLE_API_KEY", ""))

class ScoutClient:
    """
    Scout MCP client for roadmap generation.
    Directly integrates with Google Gemini for roadmap generation.
    """

    def __init__(self):
        self.model = genai.GenerativeModel('models/gemini-2.5-flash')

    def _build_roadmap_prompt(
        self,
        career_goal: str,
        current_skills: List[Dict[str, Any]],
        learning_preferences: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build a detailed prompt for roadmap generation."""

        skills_summary = "\n".join([
            f"- {skill['skill']}: Level {skill['score']}/10 ({skill['level']})"
            for skill in current_skills
        ])

        preferences_text = ""
        if learning_preferences:
            style = learning_preferences.get('learning_style', 'mixed')
            hours = learning_preferences.get('time_commitment_hours_per_week', 10)
            preferences_text = f"""
Learning Preferences:
- Learning Style: {style}
- Time Commitment: {hours} hours/week
"""

        prompt = f"""You are Scout, an AI career advisor. Generate a concise learning roadmap.

GOAL: {career_goal}
CURRENT SKILLS: {skills_summary}
{preferences_text}

CREATE a structured roadmap with 3-5 modules. Each module needs:
- Title, description, estimated hours
- Skills taught (2-4 skills)
- 2-3 quality learning resources (real URLs: YouTube, freeCodeCamp, official docs)
- 1 hands-on project
- Prerequisites (if any)
- Learning outcomes (2-3 points)

Keep it practical and achievable. Total: 8-16 weeks

OUTPUT FORMAT (strict JSON):
{{
  "title": "Roadmap title",
  "career_goal": "{career_goal}",
  "estimated_weeks": <number>,
  "modules": [
    {{
      "id": "module-1",
      "title": "Module title",
      "description": "What this module covers",
      "estimated_hours": <number>,
      "difficulty": "beginner|intermediate|advanced",
      "skills_taught": ["skill1", "skill2"],
      "prerequisite_skills": ["skill1"],
      "learning_outcomes": ["outcome1", "outcome2"],
      "resources": [
        {{
          "title": "Resource title",
          "type": "video|article|documentation|interactive-lab|book",
          "url": "https://...",
          "duration": "2 hours",
          "duration_minutes": 120,
          "difficulty": "beginner|intermediate|advanced",
          "description": "Brief description"
        }}
      ],
      "project": {{
        "title": "Project title",
        "description": "What to build",
        "estimated_hours": <number>,
        "skills_applied": ["skill1", "skill2"],
        "deliverables": ["deliverable1", "deliverable2"],
        "difficulty": "beginner|intermediate|advanced"
      }}
    }}
  ]
}}

IMPORTANT: Return ONLY valid JSON, no markdown formatting, no explanation text.
"""
        return prompt

    async def generate_roadmap(
        self,
        career_goal: str,
        current_skills: List[Dict[str, Any]],
        learning_preferences: Optional[Dict[str, Any]] = None,
        user_id: str = "anonymous"
    ) -> Dict[str, Any]:
        """Generate a personalized learning roadmap."""

        start_time = datetime.utcnow()

        try:
            # Build prompt
            prompt = self._build_roadmap_prompt(career_goal, current_skills, learning_preferences)

            # Generate with Gemini
            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean response (remove markdown code blocks if present)
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # Parse JSON
            roadmap_data = json.loads(response_text)

            # Add metadata
            roadmap_id = str(uuid.uuid4())
            roadmap = {
                "id": roadmap_id,
                "user_id": user_id,
                "title": roadmap_data.get("title", f"Roadmap to {career_goal}"),
                "career_goal": career_goal,
                "estimated_weeks": roadmap_data.get("estimated_weeks", 12),
                "modules": roadmap_data.get("modules", []),
                "current_module": 0,
                "progress_percentage": 0.0,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "roadmap": roadmap,
                "message": "Roadmap generated successfully",
                "processing_time_seconds": processing_time
            }

        except json.JSONDecodeError as e:
            print(f"JSON parse error: {e}")
            print(f"Response text: {response_text[:500]}")
            raise Exception(f"Failed to parse roadmap response: {str(e)}")
        except Exception as e:
            print(f"Roadmap generation error: {e}")
            raise Exception(f"Failed to generate roadmap: {str(e)}")

    async def update_roadmap(
        self,
        roadmap_id: str,
        user_prompt: str,
        existing_roadmap: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update an existing roadmap based on user feedback."""

        start_time = datetime.utcnow()

        try:
            prompt = f"""You are Scout, an expert career path advisor.

The user has the following existing roadmap:

{json.dumps(existing_roadmap, indent=2)}

The user wants to update it with this request:
"{user_prompt}"

Please generate an updated roadmap that incorporates the user's feedback while maintaining the same JSON structure.

IMPORTANT: Return ONLY valid JSON in the exact same format as the input roadmap, no markdown, no explanation.
"""

            response = self.model.generate_content(prompt)
            response_text = response.text.strip()

            # Clean response
            if response_text.startswith("```json"):
                response_text = response_text[7:]
            if response_text.startswith("```"):
                response_text = response_text[3:]
            if response_text.endswith("```"):
                response_text = response_text[:-3]
            response_text = response_text.strip()

            # Parse updated roadmap
            updated_roadmap = json.loads(response_text)
            updated_roadmap["id"] = roadmap_id
            updated_roadmap["updated_at"] = datetime.utcnow().isoformat()

            processing_time = (datetime.utcnow() - start_time).total_seconds()

            return {
                "roadmap": updated_roadmap,
                "message": "Roadmap updated successfully",
                "processing_time_seconds": processing_time
            }

        except Exception as e:
            print(f"Roadmap update error: {e}")
            raise Exception(f"Failed to update roadmap: {str(e)}")

# Global instance
scout_client = ScoutClient()
