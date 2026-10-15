"""Chat Agent - Handles general conversation and help requests."""

from .base import BaseAgent, AgentResponse
import config


class ChatAgent(BaseAgent):
    """Handles general conversation and system help."""
    
    HELP_MESSAGE = """
🤖 **Multi-Agent Data Assistant**

I'm a multi-agent system designed to help you explore and analyze data. Here's what I can do:

**📊 Data Queries (SQL Agent)**
- "Show me top 10 customers by spending"
- "How many products do we have?"
- "List recent orders"
- "What's our total revenue?"

**📈 Analysis (Analyst Agent)**
- "What insights can you give about sales?"
- "Analyze the customer data"
- "What trends do you see?"

**💬 General Help (Chat Agent)**
- "What can you help me with?"
- "How does this work?"

**Example Workflow:**
1. Start with a data query: "Show top 5 customers by total spending"
2. Then ask for analysis: "What patterns do you notice?"

Just type your question and I'll route it to the right specialist agent!
"""
    
    def __init__(self):
        super().__init__(
            name="Chat Agent",
            description="Handles general conversation and help"
        )
    
    def process(self, query: str, context: dict = None) -> AgentResponse:
        """Handle general queries."""
        
        query_lower = query.lower()
        
        # Help requests
        if any(kw in query_lower for kw in ["help", "what can you", "how do", "guide"]):
            return AgentResponse(
                success=True,
                message=self.HELP_MESSAGE,
                agent_name=self.name
            )
        
        # General chat with LLM
        if self.groq_client and not config.DEMO_MODE:
            response = self._generate_response(query)
        elif self.openai_client and not config.DEMO_MODE:
            response = self._generate_response(query)
        else:
            response = self._demo_chat_response(query)
        
        return AgentResponse(
            success=True,
            message=response,
            agent_name=self.name
        )
    
    def _generate_response(self, query: str) -> str:
        """Generate conversational response."""
        system_prompt = """You are a helpful data assistant. You help users explore and understand data.

If the user asks something that should involve data queries, gently guide them to ask in a way 
that can be converted to SQL (e.g., "show me...", "how many...", "list...").

Keep responses friendly and concise."""

        return self._call_llm(system_prompt, query)
    
    def _demo_chat_response(self, query: str) -> str:
        """Demo mode response."""
        return f"""💬 **Chat Response** (Demo Mode)

I received your message: "{query}"

I'm currently running in demo mode without an API key. Here's what I can still help with:

1. **Data Queries** - Try asking things like:
   - "Show me top 5 customers"
   - "How many orders do we have?"
   - "List all products"

2. **Help** - Type "help" to see all my capabilities

*For full conversational AI, add your OpenAI API key.*
"""
