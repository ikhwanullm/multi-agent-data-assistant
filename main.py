"""
Multi-Agent Data Assistant - Main Orchestrator

This module coordinates multiple specialized agents to handle natural language
queries about data. It demonstrates a production-like multi-agent architecture.

Author: Ikhwanul Muslimin
"""

from typing import Optional
from agents import RouterAgent, SQLAgent, AnalystAgent, ChatAgent
from agents.base import AgentResponse
from tools.database import setup_database
import config
from pathlib import Path


class MultiAgentOrchestrator:
    """Orchestrates multiple agents to handle user queries."""
    
    def __init__(self):
        self.router = RouterAgent()
        self.sql_agent = SQLAgent()
        self.analyst_agent = AnalystAgent()
        self.chat_agent = ChatAgent()
        
        # Store context for follow-up queries
        self.context = {}
    
    def process(self, query: str) -> AgentResponse:
        """Process a user query through the multi-agent system."""
        
        # Step 1: Route the query
        routing = self.router.process(query)
        agent_type = routing.data["agent_type"]
        confidence = routing.data["confidence"]
        
        # Step 2: Execute with appropriate agent
        if agent_type == "sql":
            response = self.sql_agent.process(query)
            # Store results in context for potential follow-up analysis
            if response.success and response.data:
                self.context["last_results"] = response.data.get("results", [])
                self.context["last_sql"] = response.data.get("sql", "")
        
        elif agent_type == "analyst":
            # Pass context from previous queries
            context = {
                "data": self.context.get("last_results", []),
                "sql": self.context.get("last_sql", "")
            }
            response = self.analyst_agent.process(query, context)
        
        else:  # chat or help
            response = self.chat_agent.process(query)
        
        # Add routing info to response
        response.data = response.data or {}
        response.data["routed_to"] = agent_type
        response.data["routing_confidence"] = confidence
        
        return response


def main():
    """CLI interface for the multi-agent system."""
    print("\n" + "="*60)
    print("🤖 Multi-Agent Data Assistant")
    print("="*60)
    
    # Check if database exists, if not create it
    if not config.DATABASE_PATH.exists():
        print("\n📊 Setting up sample database...")
        setup_database()
    
    # Check mode
    if config.DEMO_MODE:
        print("\n⚠️  Running in DEMO MODE (no API key detected)")
        print("   Set OPENAI_API_KEY for full AI capabilities")
    else:
        print(f"\n✅ Using OpenAI model: {config.OPENAI_MODEL}")
    
    print("\nType 'help' for usage guide, 'quit' to exit")
    print("-"*60)
    
    orchestrator = MultiAgentOrchestrator()
    
    while True:
        try:
            query = input("\n🔍 You: ").strip()
            
            if not query:
                continue
            
            if query.lower() in ["quit", "exit", "q"]:
                print("\n👋 Goodbye!")
                break
            
            # Process query
            response = orchestrator.process(query)
            
            # Display response
            print(f"\n🤖 [{response.agent_name}]")
            print("-"*40)
            print(response.message)
            
            # Show data if available
            if response.data and "results" in response.data:
                results = response.data["results"]
                if results:
                    print(f"\n📋 Results ({len(results)} rows):")
                    for i, row in enumerate(results[:10]):
                        print(f"   {i+1}. {row}")
                    if len(results) > 10:
                        print(f"   ... and {len(results) - 10} more rows")
            
            # Show SQL if generated
            if response.data and "sql" in response.data:
                print(f"\n💾 SQL: {response.data['sql']}")
                
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
