"""Router Agent - Classifies intent and routes to appropriate specialist agent."""

import re
from typing import Tuple
from .base import BaseAgent, AgentResponse


class RouterAgent(BaseAgent):
    """Routes queries to the appropriate specialist agent."""
    
    # Keywords for each agent type
    SQL_KEYWORDS = [
        "show", "list", "get", "find", "select", "count", "how many",
        "total", "sum", "average", "top", "bottom", "highest", "lowest",
        "customers", "products", "orders", "sales", "revenue"
    ]
    
    ANALYST_KEYWORDS = [
        "analyze", "insight", "trend", "pattern", "why", "explain",
        "recommend", "suggest", "compare", "forecast", "predict"
    ]
    
    HELP_KEYWORDS = [
        "help", "what can you", "how do i", "guide", "tutorial",
        "capabilities", "features"
    ]
    
    RESUME_KEYWORDS = [
        "ikhwan", "resume", "cv", "experience", "background", "qualification",
        "education", "skill", "certification", "award", "achievement",
        "career", "work history", "who are you", "who is", "tell me about you",
        "your experience", "your skill", "your education", "your background",
        "nexora", "bri", "waresix", "itb", "bandung", "physics"
    ]
    
    def __init__(self):
        super().__init__(
            name="Router Agent",
            description="Classifies user intent and routes to specialist agents"
        )
    
    def process(self, query: str, context: dict = None) -> AgentResponse:
        """Determine which agent should handle the query."""
        agent_type, confidence = self._classify_intent(query)
        
        return AgentResponse(
            success=True,
            message=f"Routing to {agent_type}",
            data={"agent_type": agent_type, "confidence": confidence},
            agent_name=self.name,
            confidence=confidence
        )
    
    def _classify_intent(self, query: str) -> Tuple[str, float]:
        """Classify query intent using keyword matching + LLM."""
        query_lower = query.lower()
        
        # Keyword-based scoring
        sql_score = self._keyword_score(query_lower, self.SQL_KEYWORDS)
        analyst_score = self._keyword_score(query_lower, self.ANALYST_KEYWORDS)
        help_score = self._keyword_score(query_lower, self.HELP_KEYWORDS)
        resume_score = self._keyword_score(query_lower, self.RESUME_KEYWORDS)
        
        # Determine winner
        scores = {
            "sql": sql_score,
            "analyst": analyst_score,
            "help": help_score,
            "resume": resume_score,
            "chat": 0.3  # Default fallback score
        }
        
        # If scores are close, use LLM for better classification
        max_score = max(scores.values())
        if max_score < 0.5 and (self.groq_client or self.openai_client):
            return self._llm_classify(query)
        
        best_agent = max(scores, key=scores.get)
        return best_agent, scores[best_agent]
    
    def _keyword_score(self, query: str, keywords: list) -> float:
        """Calculate keyword match score."""
        matches = sum(1 for kw in keywords if kw in query)
        return min(matches / 3, 1.0)  # Cap at 1.0
    
    def _llm_classify(self, query: str) -> Tuple[str, float]:
        """Use LLM for intent classification when keywords aren't clear."""
        system_prompt = """You are an intent classifier. Classify the user query into one of these categories:
- sql: Questions that need database queries (show data, count, list, etc.)
- analyst: Questions asking for insights, trends, or analysis
- resume: Questions about Ikhwan Muslimin's background, experience, skills, education, or career
- help: Questions about how to use the system
- chat: General conversation or unclear intent

Respond with only the category name, nothing else."""

        result = self._call_llm(system_prompt, query)
        result = result.strip().lower()
        
        if result in ["sql", "analyst", "resume", "help", "chat"]:
            return result, 0.8
        return "chat", 0.5
