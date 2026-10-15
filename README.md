# 🤖 Multi-Agent Data Assistant

A lightweight multi-agent system for natural language data queries. Built as a portfolio demonstration of AI agent architecture patterns.

![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red)
![License](https://img.shields.io/badge/License-MIT-green)

## 🎯 What This Demonstrates

- **Multi-Agent Architecture**: 5 specialized agents working together
- **Agent Routing**: Intent classification to route queries to the right agent
- **Tool Calling**: Agents executing SQL queries as tools
- **Resume RAG**: Personal information retrieval from embedded resume data
- **Graceful Fallbacks**: Works with Groq (free), OpenAI, or demo mode

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      User Query                              │
│             "Tell me about Ikhwan's experience"              │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   🎯 Router Agent                            │
│         Classifies intent & routes to specialist            │
└─────────────────────┬───────────────────────────────────────┘
                      │
    ┌─────────────────┼─────────────────┬─────────────────┐
    ▼                 ▼                 ▼                 ▼
┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐
│📊 SQL   │    │📈Analyst│    │📄Resume │    │💬 Chat  │    │❓ Help  │
│ Agent   │    │ Agent   │    │ Agent   │    │ Agent   │    │ Agent   │
└────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘    └────┬────┘
     │              │              │              │              │
     └──────────────┴──────────────┴──────────────┴──────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   📋 Response                                │
│              Formatted answer to user                        │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Option 1: With Groq API (Recommended - Free & Fast)

```bash
# Clone and setup
cd multi-agent-data-assistant
pip install -r requirements.txt

# Set API key (get free key at console.groq.com)
export GROQ_API_KEY="your-groq-key"   # Linux/Mac
set GROQ_API_KEY=your-groq-key        # Windows CMD
$env:GROQ_API_KEY="your-groq-key"     # Windows PowerShell

# Or create .env file
echo "GROQ_API_KEY=your-groq-key" > .env

# Run
streamlit run app.py
```

### Option 2: With OpenAI API (Fallback)

```bash
pip install -r requirements.txt
export OPENAI_API_KEY="your-openai-key"
streamlit run app.py
```

### Option 3: Demo Mode (No API Key Required)

```bash
pip install -r requirements.txt
streamlit run app.py
# App will run in demo mode with pattern-based responses
```

## 📁 Project Structure

```
multi-agent-data-assistant/
├── app.py                 # Streamlit web interface
├── main.py                # CLI interface & orchestrator
├── requirements.txt       # Python dependencies
├── agents/
│   ├── __init__.py
│   ├── base.py            # Base agent class
│   ├── router.py          # Intent classification agent
│   ├── sql_agent.py       # SQL generation & execution
│   ├── analyst_agent.py   # Data analysis & insights
│   └── chat_agent.py      # General conversation
├── tools/
│   ├── __init__.py
│   └── database.py        # SQLite database tools
├── data/
│   └── sample.db          # Sample e-commerce database
└── config.py              # Configuration settings
```

## 💾 Sample Database Schema

The included SQLite database simulates an e-commerce platform:

```sql
-- Customers table
CREATE TABLE customers (
    id INTEGER PRIMARY KEY,
    name TEXT,
    email TEXT,
    city TEXT,
    created_at DATE
);

-- Products table  
CREATE TABLE products (
    id INTEGER PRIMARY KEY,
    name TEXT,
    category TEXT,
    price REAL,
    stock INTEGER
);

-- Orders table
CREATE TABLE orders (
    id INTEGER PRIMARY KEY,
    customer_id INTEGER,
    product_id INTEGER,
    quantity INTEGER,
    total_amount REAL,
    order_date DATE,
    status TEXT
);
```

## 🎮 Example Queries

| Query | Routed To | What Happens |
|-------|-----------|--------------|
| "Show me top 5 customers by total spending" | SQL Agent | Generates & executes SQL |
| "What insights can you give about sales trends?" | Analyst Agent | Analyzes data patterns |
| "Tell me about Ikhwan's experience" | Resume Agent | Answers from resume data |
| "What skills does Ikhwan have?" | Resume Agent | Lists technical skills |
| "What can you help me with?" | Help Agent | Explains capabilities |
| "Tell me about this system" | Chat Agent | General conversation |

## 🔧 Configuration

Edit `config.py` to customize:

```python
# LLM Provider Priority: Groq -> OpenAI -> Demo Mode
# Groq is used by default if GROQ_API_KEY is set

# Groq settings (Primary - Free & Fast)
GROQ_MODEL = "openai/gpt-oss-20b"  # Fast, affordable

# OpenAI settings (Fallback)
OPENAI_MODEL = "gpt-4o-mini"

# Database path
DATABASE_PATH = "data/sample.db"
```

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `GROQ_API_KEY` | Groq API key (free at console.groq.com) | Recommended |
| `OPENAI_API_KEY` | OpenAI API key (fallback) | Optional |

## 🧪 Running Tests

```bash
python -m pytest tests/ -v
```

## 📊 Agent Details

### Router Agent
- **Purpose**: Classify user intent and route to appropriate specialist
- **Method**: Keyword matching + LLM classification (when available)
- **Outputs**: Agent selection + confidence score

### SQL Agent
- **Purpose**: Convert natural language to SQL queries
- **Tools**: SQLite query execution
- **Safety**: Read-only queries, schema validation

### Analyst Agent
- **Purpose**: Provide insights and analysis on query results
- **Method**: Statistical analysis + LLM interpretation
- **Outputs**: Trends, patterns, recommendations

### Chat Agent
- **Purpose**: Handle general questions and conversation
- **Fallback**: Default agent when others don't match

## 🚢 Deployment Options

### Streamlit Cloud (Easiest)
1. Push to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo and deploy
4. Add `OPENAI_API_KEY` in Secrets

### Docker
```bash
docker build -t multi-agent-assistant .
docker run -p 8501:8501 -e OPENAI_API_KEY=your-key multi-agent-assistant
```

### Hugging Face Spaces
1. Create new Space (Streamlit SDK)
2. Upload files
3. Add API key in Settings > Secrets

## 👤 Author

**Ikhwanul Muslimin**  
Data Scientist @ BRI | AI Agent Systems

- LinkedIn: [ikhwanulmuslimin](https://linkedin.com/in/ikhwanulmuslimin)
- GitHub: [waannuullll](https://github.com/waannuullll)

## 📝 License

MIT License - feel free to use for learning and portfolio purposes.

---

*This project demonstrates multi-agent architecture patterns similar to production systems I've built at BRI, including NEXORA (5-agent enterprise chatbot) and automated code migration systems.*
