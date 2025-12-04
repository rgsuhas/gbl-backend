from neo4j import GraphDatabase
import os
from typing import Optional, List, Dict, Any

class Neo4jClient:
    def __init__(self):
        uri = os.getenv("NEO4J_URI")
        username = os.getenv("NEO4J_USERNAME")
        password = os.getenv("NEO4J_PASSWORD")

        if not all([uri, username, password]):
            print("Warning: Neo4j credentials not configured. Using mock mode.")
            self.driver = None
            self.mock_mode = True
        else:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
            self.mock_mode = False

    def close(self):
        """Close the driver connection."""
        if self.driver:
            self.driver.close()

    def get_related_skills(self, skill_name: str, limit: int = 10) -> List[str]:
        """Get skills related to the given skill."""
        if self.mock_mode:
            # Return mock data for demo purposes
            mock_skills = {
                "Python": ["Django", "Flask", "FastAPI", "Data Analysis", "Machine Learning"],
                "JavaScript": ["React", "Node.js", "TypeScript", "Vue.js", "Angular"],
                "React": ["JavaScript", "TypeScript", "Redux", "Next.js", "HTML/CSS"],
                "Machine Learning": ["Python", "TensorFlow", "PyTorch", "Data Science", "Statistics"],
            }
            return mock_skills.get(skill_name, ["Data Analysis", "Problem Solving", "Communication"])

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (s:Skill {name: $skill_name})-[:RELATED_TO|REQUIRES]-(related:Skill)
                RETURN related.name as skill
                LIMIT $limit
                """,
                skill_name=skill_name,
                limit=limit
            )
            return [record["skill"] for record in result]

    def get_skill_prerequisites(self, skill_name: str) -> List[str]:
        """Get prerequisite skills for the given skill."""
        if self.mock_mode:
            mock_prereqs = {
                "React": ["JavaScript", "HTML/CSS"],
                "Django": ["Python", "Web Development Basics"],
                "Machine Learning": ["Python", "Statistics", "Linear Algebra"],
                "FastAPI": ["Python", "REST APIs"],
            }
            return mock_prereqs.get(skill_name, [])

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (s:Skill {name: $skill_name})<-[:REQUIRES]-(prereq:Skill)
                RETURN prereq.name as skill
                """,
                skill_name=skill_name
            )
            return [record["skill"] for record in result]

    def get_skill_learning_path(self, start_skill: str, target_skill: str) -> List[str]:
        """Find a learning path between two skills."""
        if self.mock_mode:
            return [start_skill, "Intermediate Skill", target_skill]

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH path = shortestPath(
                    (start:Skill {name: $start_skill})-[:RELATED_TO|REQUIRES*]-(target:Skill {name: $target_skill})
                )
                RETURN [node in nodes(path) | node.name] as skills
                """,
                start_skill=start_skill,
                target_skill=target_skill
            )
            record = result.single()
            return record["skills"] if record else []

    def search_skills(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for skills matching the query."""
        if self.mock_mode:
            mock_results = [
                {"name": "Python Programming", "category": "Programming"},
                {"name": "JavaScript Development", "category": "Programming"},
                {"name": "Machine Learning", "category": "Data Science"},
                {"name": "React Development", "category": "Web Development"},
                {"name": "Data Analysis", "category": "Data Science"},
            ]
            return [s for s in mock_results if query.lower() in s["name"].lower()][:limit]

        with self.driver.session() as session:
            result = session.run(
                """
                MATCH (s:Skill)
                WHERE s.name CONTAINS $query OR s.category CONTAINS $query
                RETURN s.name as name, s.category as category
                LIMIT $limit
                """,
                query=query,
                limit=limit
            )
            return [{"name": record["name"], "category": record["category"]} for record in result]

# Global instance
neo4j_client = Neo4jClient()
