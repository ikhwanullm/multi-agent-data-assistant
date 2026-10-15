"""Quick test to verify agents work correctly."""

import sys
sys.path.insert(0, '.')

from agents import RouterAgent, SQLAgent, AnalystAgent, ChatAgent, ResumeAgent
from tools.database import setup_database
import config

def test_router():
    print("Testing Router Agent...")
    router = RouterAgent()
    
    tests = [
        ("Show top 5 customers", "sql"),
        ("What insights do you see?", "analyst"),
        ("Help me", "help"),
        ("Tell me about Ikhwan's experience", "resume"),
        ("What skills does Ikhwan have?", "resume"),
    ]
    
    for query, expected in tests:
        result = router.process(query)
        actual = result.data["agent_type"]
        status = "[OK]" if actual == expected else "[FAIL]"
        print(f"  {status} '{query}' -> {actual} (expected: {expected})")

def test_sql_agent():
    print("\nTesting SQL Agent...")
    sql_agent = SQLAgent()
    
    queries = [
        "Show top 5 customers by spending",
        "How many products do we have",
        "List recent orders",
    ]
    
    for query in queries:
        result = sql_agent.process(query)
        status = "[OK]" if result.success else "[FAIL]"
        data_count = len(result.data.get("results", [])) if result.data else 0
        print(f"  {status} '{query}' -> {data_count} results")
        if result.data and "sql" in result.data:
            print(f"       SQL: {result.data['sql'][:60]}...")

def test_analyst():
    print("\nTesting Analyst Agent...")
    analyst = AnalystAgent()
    
    # Test with sample data
    context = {
        "data": [{"name": "Test", "total": 1000}],
        "sql": "SELECT * FROM test"
    }
    result = analyst.process("What insights can you give?", context)
    status = "[OK]" if result.success else "[FAIL]"
    print(f"  {status} Analysis generated: {len(result.message)} chars")

def test_chat():
    print("\nTesting Chat Agent...")
    chat = ChatAgent()
    
    result = chat.process("help")
    status = "[OK]" if result.success and "Multi-Agent" in result.message else "[FAIL]"
    print(f"  {status} Help message generated")

def test_resume():
    print("\nTesting Resume Agent...")
    resume = ResumeAgent()
    
    queries = [
        "Tell me about Ikhwan's experience",
        "What skills does Ikhwan have?",
        "What awards has Ikhwan won?",
    ]
    
    for query in queries:
        result = resume.process(query)
        status = "[OK]" if result.success and len(result.message) > 50 else "[FAIL]"
        print(f"  {status} '{query}' -> {len(result.message)} chars")

if __name__ == "__main__":
    print("="*50)
    print("Multi-Agent Data Assistant - Quick Test")
    print("="*50)
    print(f"Demo Mode: {config.DEMO_MODE}")
    print(f"LLM Provider: {config.LLM_PROVIDER}")
    print()
    
    test_router()
    test_sql_agent()
    test_analyst()
    test_chat()
    test_resume()
    
    print("\n" + "="*50)
    print("Tests completed!")
    print("="*50)
