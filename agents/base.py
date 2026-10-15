"""Base agent class with common functionality."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Optional
import config

# Optional imports for LLM providers
try:
    from groq import Groq
    GROQ_AVAILABLE = True
except ImportError:
    Groq = None
    GROQ_AVAILABLE = False

try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    openai = None
    OPENAI_AVAILABLE = False


@dataclass
class AgentResponse:
    """Standardized response from any agent."""
    success: bool
    message: str
    data: Optional[Any] = None
    agent_name: str = ""
    confidence: float = 1.0


class BaseAgent(ABC):
    """Abstract base class for all agents."""
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.groq_client = None
        self.openai_client = None
        self.provider = config.LLM_PROVIDER
        
        # Initialize Groq client (primary)
        if GROQ_AVAILABLE and config.GROQ_API_KEY:
            self.groq_client = Groq(api_key=config.GROQ_API_KEY)
        
        # Initialize OpenAI client (fallback)
        if OPENAI_AVAILABLE and config.OPENAI_API_KEY:
            self.openai_client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
    
    @abstractmethod
    def process(self, query: str, context: Optional[dict] = None) -> AgentResponse:
        """Process a query and return response."""
        pass
    
    def _call_llm(self, system_prompt: str, user_message: str) -> str:
        """Call LLM API with fallback support."""
        
        # Try Groq first (fast & free)
        if self.groq_client and self.provider == "groq":
            try:
                response = self.groq_client.chat.completions.create(
                    model=config.GROQ_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            except Exception as e:
                print(f"Groq error, falling back: {e}")
        
        # Fallback to OpenAI
        if self.openai_client:
            try:
                response = self.openai_client.chat.completions.create(
                    model=config.OPENAI_MODEL,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_message}
                    ],
                    temperature=0.3,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            except Exception as e:
                return f"Error calling OpenAI: {str(e)}"
        
        # Demo mode fallback
        return self._demo_response(user_message)
    
    def _demo_response(self, query: str) -> str:
        """Fallback response for demo mode."""
        return f"[Demo Mode] Processing: {query}"
