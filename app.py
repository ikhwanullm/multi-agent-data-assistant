"""
Multi-Agent Data Assistant - Streamlit Web Interface

A visual interface for the multi-agent system with real-time 
agent routing visualization.

Author: Ikhwanul Muslimin
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from agents import RouterAgent, SQLAgent, AnalystAgent, ChatAgent, ResumeAgent
from tools.database import setup_database
import config
import pandas as pd


# Page config
st.set_page_config(
    page_title="Multi-Agent Data Assistant",
    page_icon="🤖",
    layout="wide"
)


WELCOME_MESSAGE = """
👋 **Welcome! I'm a Multi-Agent AI Assistant** built by Ikhwanul Muslimin.

I have **5 specialized agents** that can help you with different tasks:

| Agent | What it does | Try asking... |
|-------|--------------|---------------|
| 🟦 **SQL** | Query the e-commerce database | "Show top 5 customers by spending" |
| 🟩 **Analyst** | Analyze data & provide insights | "What insights can you give?" |
| 🟧 **Resume** | Answer questions about me (Ikhwan) | "Tell me about your AI experience" |
| 🟨 **Chat** | General conversation | "Hello!" |
| 🟪 **Help** | Guide you on how to use this | "Help" |

---

**📊 Available Data:**
This demo includes a sample e-commerce database with:
- **15 customers** (Indonesian names, various cities)
- **15 products** (Electronics & Fashion, Rp 800K - 20M)
- **100 orders** (various statuses: pending, shipped, delivered)

---

**💡 Quick Start - Try one of these:**
1. `"Show me top 5 customers by total spending"`
2. `"How many products do we have in Electronics category?"`
3. `"Tell me about Ikhwan's experience with AI agents"`
4. `"What awards has Ikhwan won?"`

Just type your question below! 👇
"""


def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []
        # Add welcome message on first load
        st.session_state.messages.append({
            "role": "assistant",
            "content": WELCOME_MESSAGE,
            "agent_type": "welcome",
            "confidence": 1.0
        })
    if "context" not in st.session_state:
        st.session_state.context = {}
    if "agents_initialized" not in st.session_state:
        st.session_state.router = RouterAgent()
        st.session_state.sql_agent = SQLAgent()
        st.session_state.analyst_agent = AnalystAgent()
        st.session_state.chat_agent = ChatAgent()
        st.session_state.resume_agent = ResumeAgent()
        st.session_state.agents_initialized = True


def ensure_database():
    """Ensure database exists."""
    if not config.DATABASE_PATH.exists():
        setup_database()


def process_query(query: str) -> dict:
    """Process query through multi-agent system."""
    
    # Route
    routing = st.session_state.router.process(query)
    agent_type = routing.data["agent_type"]
    confidence = routing.data["confidence"]
    
    # Execute
    if agent_type == "sql":
        response = st.session_state.sql_agent.process(query)
        if response.success and response.data:
            st.session_state.context["last_results"] = response.data.get("results", [])
            st.session_state.context["last_sql"] = response.data.get("sql", "")
    
    elif agent_type == "analyst":
        context = {
            "data": st.session_state.context.get("last_results", []),
            "sql": st.session_state.context.get("last_sql", "")
        }
        response = st.session_state.analyst_agent.process(query, context)
    
    elif agent_type == "resume":
        response = st.session_state.resume_agent.process(query)
    
    else:
        response = st.session_state.chat_agent.process(query)
    
    return {
        "agent_type": agent_type,
        "confidence": confidence,
        "response": response
    }


def render_agent_badge(agent_type: str, confidence: float):
    """Render agent type badge."""
    colors = {
        "sql": "🟦",
        "analyst": "🟩", 
        "chat": "🟨",
        "help": "🟪",
        "resume": "🟧",
        "welcome": "👋"
    }
    names = {
        "sql": "SQL Agent",
        "analyst": "Analyst Agent",
        "chat": "Chat Agent",
        "help": "Help Agent",
        "resume": "Resume Agent",
        "welcome": "Welcome"
    }
    
    color = colors.get(agent_type, "⬜")
    name = names.get(agent_type, agent_type)
    
    st.caption(f"{color} Routed to **{name}** (confidence: {confidence:.0%})")


def main():
    # Initialize
    init_session_state()
    ensure_database()
    
    # Header
    st.title("🤖 Multi-Agent Data Assistant")
    st.caption("A portfolio demo by Ikhwanul Muslimin — showcasing multi-agent AI architecture")
    
    # Sidebar
    with st.sidebar:
        st.header("About This Demo")
        st.markdown("""
        **Multi-Agent Data Assistant** demonstrates how multiple AI agents 
        can work together to handle different types of queries.
        
        Built by [Ikhwanul Muslimin](https://linkedin.com/in/ikhwanulmuslimin) 
        as a portfolio project showcasing AI agent architecture.
        """)
        
        st.divider()
        
        # Data Overview
        st.header("📊 Sample Data")
        st.markdown("""
        **E-commerce Database:**
        - `customers` - 15 Indonesian customers
        - `products` - 15 items (Electronics & Fashion)
        - `orders` - 100 transactions
        
        **Schema:**
        ```
        customers: id, name, email, city
        products: id, name, category, price
        orders: id, customer_id, product_id, 
                quantity, total_amount, status
        ```
        """)
        
        st.divider()
        
        st.header("🤖 Agents")
        st.markdown("""
        - 🟦 **SQL** - Query database
        - 🟩 **Analyst** - Data insights  
        - 🟧 **Resume** - About Ikhwan
        - 🟨 **Chat** - General talk
        - 🟪 **Help** - Usage guide
        """)
        
        st.divider()
        
        # Mode indicator
        if config.DEMO_MODE:
            st.warning("**Demo Mode**\nNo API key detected. Using pattern matching.")
        elif config.LLM_PROVIDER == "groq":
            st.success(f"**Groq API**\nModel: {config.GROQ_MODEL}")
        else:
            st.success(f"**OpenAI API**\nModel: {config.OPENAI_MODEL}")
        
        st.divider()
        
        st.header("💡 Try These")
        
        st.caption("**Data Queries:**")
        examples_data = [
            "Show top 5 customers by spending",
            "List products in Electronics category",
            "How many orders are pending?",
        ]
        for ex in examples_data:
            if st.button(f"📊 {ex}", key=f"ex_data_{ex}"):
                st.session_state.example_query = ex
        
        st.caption("**About Me (Ikhwan):**")
        examples_resume = [
            "Tell me about your AI agent experience",
            "What skills do you have?",
            "What awards have you won?",
        ]
        for ex in examples_resume:
            if st.button(f"👤 {ex}", key=f"ex_resume_{ex}"):
                st.session_state.example_query = ex
        
        # Keep this for backwards compatibility
        examples = examples_data + examples_resume
        st.divider()
        
        if st.button("🗑️ Clear & Restart"):
            st.session_state.messages = [{
                "role": "assistant",
                "content": WELCOME_MESSAGE,
                "agent_type": "welcome",
                "confidence": 1.0
            }]
            st.session_state.context = {}
            st.rerun()
    
    # Main chat area
    chat_container = st.container()
    
    # Display chat history
    with chat_container:
        for msg in st.session_state.messages:
            if msg["role"] == "user":
                with st.chat_message("user"):
                    st.write(msg["content"])
            else:
                with st.chat_message("assistant"):
                    if "agent_type" in msg:
                        render_agent_badge(msg["agent_type"], msg["confidence"])
                    st.write(msg["content"])
                    
                    # Show data table if available
                    if "data" in msg and msg["data"]:
                        with st.expander("📊 View Data"):
                            df = pd.DataFrame(msg["data"])
                            st.dataframe(df, use_container_width=True)
                    
                    # Show SQL if available
                    if "sql" in msg and msg["sql"]:
                        with st.expander("💾 View SQL"):
                            st.code(msg["sql"], language="sql")
    
    # Input
    query = st.chat_input("Ask me anything about the data...")
    
    # Handle example button clicks
    if hasattr(st.session_state, "example_query"):
        query = st.session_state.example_query
        del st.session_state.example_query
    
    if query:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": query})
        
        # Process
        with st.spinner("🔄 Processing..."):
            result = process_query(query)
        
        # Add assistant response
        response = result["response"]
        assistant_msg = {
            "role": "assistant",
            "content": response.message,
            "agent_type": result["agent_type"],
            "confidence": result["confidence"]
        }
        
        if response.data:
            if "results" in response.data:
                assistant_msg["data"] = response.data["results"]
            if "sql" in response.data:
                assistant_msg["sql"] = response.data["sql"]
        
        st.session_state.messages.append(assistant_msg)
        st.rerun()
    
    # Footer
    st.divider()
    st.markdown("""
    <div style='text-align: center; color: gray;'>
    Built by <a href='https://linkedin.com/in/ikhwanulmuslimin'>Ikhwanul Muslimin</a> | 
    <a href='https://github.com/waannuullll'>GitHub</a>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
