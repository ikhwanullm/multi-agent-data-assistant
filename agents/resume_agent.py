"""Resume Agent - Answers questions about Ikhwan's background and experience."""

from .base import BaseAgent, AgentResponse
import config


class ResumeAgent(BaseAgent):
    """Answers questions about Ikhwan Muslimin's resume and experience."""
    
    RESUME_DATA = """
# IKHWANUL MUSLIMIN - Resume

## Contact
- Location: Jakarta, Indonesia
- Email: ikhwan.1998@gmail.com
- Phone: 087749357454
- LinkedIn: linkedin.com/in/ikhwanulmuslimin
- GitHub: github.com/waannuullll
- Kaggle: kaggle.com/ikhwanulmuslimin

## Professional Summary
Data Scientist specializing in AI agent systems with 4+ years at BRI, one of Southeast Asia's largest banks. Built and deployed two production multi-agent systems: NEXORA, an enterprise data chatbot with 5 specialized agents serving 2,000+ data sources, and a multi-agent code migration system that cut Spark/CML delivery time by 87%. Proven track record in graph AI (Neo4j recommender with 22% conversion lift) and anomaly detection at 100M+ transaction scale. Employee of the Year 2025. MSc Physics, ITB (best graduate, GPA 3.92).

## Skills

### AI Agents & LLM Systems
- Multi-Agent Orchestration: Agent routing, task decomposition, 5-agent production system
- RAG (Retrieval-Augmented Generation): Semantic search, document retrieval, query understanding
- LLM Deployment: Self-hosted Qwen, Amazon Bedrock, GPT models
- Agent Tooling: Kiro, Dataiku, tool calling, prompt engineering

### Machine Learning & Graph AI
- Graph Neural Networks (GNN), Knowledge Graphs
- Recommender Systems, Anomaly Detection, Cluster Analysis
- Neo4j, TigerGraph, Graph Databases

### Programming & Data Platforms
- Languages: Python, SQL, PostgreSQL, HTML
- Platforms: Cloudera, Cloudera Machine Learning (CML), Apache Spark, Amazon Bedrock, Dataiku, AtScale, Confluent

### Languages
- English (Professional Working)
- Bahasa Indonesia (Native)

## Experience

### PT Bank Rakyat Indonesia (Persero) Tbk | Jakarta, Indonesia
**Data Scientist Junior Manager** | September 2023 - Present

AI Agent Development:
- Architected NEXORA, a production Indonesian-language data chatbot with 5 specialized agents (query router, SQL generator, data validator, response formatter, feedback handler) orchestrated via Amazon Bedrock
- Implemented RAG pipeline on Dataiku connecting 2,000+ enterprise data sources with semantic search
- Designed agent routing logic that matches user intent to specialist agents; expected to serve 100+ users
- Built a multi-agent code migration system using Kiro and self-hosted Qwen LLM with dedicated agents for code analysis, refactoring, testing, and deployment; reduced Spark/CML migration time by 87%

Graph AI & Recommender Systems:
- Built a Neo4j graph-based product recommender for BRI's retail customers, lifting product conversion by 22%
- Developed graph models exposing fraud and credit risk patterns traditional ML misses, improving fraud detection by 18%

Analytics & Infrastructure:
- Shipped a self-serve analytics platform that cut analyst ad-hoc requests by 45%

**Data Scientist Trainee** | March 2023 - September 2023
- Built anomaly detection models screening 100M+ transactions/month for irregular patterns
- Analyzed ecosystem profitability to guide product and segment prioritization

**BRILiaN Future Leader Program (BFLP) IT, Batch 9** | September 2022 - September 2023
- Graduated top of batch in a one-year leadership and technology program

### Waresix | Jakarta, Indonesia
**Junior Data Analyst** | October 2021 - August 2022
- Built dashboards and reporting systems for logistics insights
- Delivered near-error-free insurance reporting

**Data Analyst Intern** | July 2021 - October 2021
- Optimized SQL queries, achieving 60% reduction in query execution time

### dibimbing.id
**Data Science Instructor** | August 2021 - November 2021
- Mentored 20+ students in data analysis, machine learning, and SQL

### Institut Teknologi Bandung (ITB)
**Research Assistant** | May 2020 - October 2021
- Conducted research on electromagnetic interactions at Magnetic and Photonic Physics Laboratory

**Teaching Assistant** | July 2019 - May 2021
- Taught Physics to 200+ undergraduate students

## Education

### Institut Teknologi Bandung
**Master of Science (MS), Physics** | August 2020 - October 2021
- GPA 3.92, graduated as best student in program

**Bachelor of Science (BS), Physics** | 2016 - 2020
- Dean's List (FMIPA ITB): five semesters, 2016-2019

## Certifications
- Neo4j Developer
- Dataiku Developer
- TigerGraph Developer
- Cloudera Developer

## Awards
- Employee of the Year, BRI Big Data & Advanced Analytics Team (2025)
- Most Creative AI App, Confluent AI Day Hackathon (2025)
- Semifinalist, Bank Indonesia Hackathon 2025 (Top 30 of 2,336 teams)
- Semifinalist, TrackAML Hackathon (2025)
- Finalist, Data Science Weekend (2023)

## Key Projects

### NEXORA - Enterprise Data Chatbot
Tech Stack: Amazon Bedrock, Dataiku, RAG, Multi-Agent System
Multi-agent chatbot enabling non-technical users to query enterprise data in natural Indonesian language.
Architecture includes 5 agents: Query Router, SQL Generator, Data Validator, Response Formatter, Feedback Handler.
Impact: Expected to serve 100+ users, reducing data discovery time from days to minutes.

### Multi-Agent Code Migration System
Tech Stack: Kiro, Qwen LLM (self-hosted), Python, Spark
Automated migration of legacy Spark and Python workloads to Cloudera Machine Learning (CML).
Agent architecture: Code Analyzer, Refactoring Agent, Testing Agent, Deployment Agent.
Impact: Reduced migration timeline by 87% (from years to months).

### Graph-Based Product Recommender
Tech Stack: Neo4j, Python, Graph Algorithms
Recommendation engine leveraging customer-product relationship graphs.
Impact: 22% lift in product conversion for BRI retail customers.
"""
    
    def __init__(self):
        super().__init__(
            name="Resume Agent",
            description="Answers questions about Ikhwan Muslimin's background and experience"
        )
    
    def process(self, query: str, context: dict = None) -> AgentResponse:
        """Answer questions about resume/background."""
        
        # Generate response using LLM with resume context
        response = self._generate_response(query)
        
        return AgentResponse(
            success=True,
            message=response,
            data={"query": query, "source": "resume"},
            agent_name=self.name
        )
    
    def _generate_response(self, query: str) -> str:
        """Generate response based on resume data."""
        
        if config.DEMO_MODE or (not self.groq_client and not self.openai_client):
            return self._demo_response(query)
        
        system_prompt = f"""You are a helpful assistant that answers questions about Ikhwanul Muslimin based on his resume data.

{self.RESUME_DATA}

Guidelines:
1. Answer questions accurately based on the resume data above
2. Be specific with numbers, dates, and achievements when available
3. If asked about something not in the resume, say you don't have that information
4. Keep responses concise but informative (2-4 sentences for simple questions, more for detailed ones)
5. Highlight relevant achievements and metrics when appropriate
6. You can refer to Ikhwan in third person ("Ikhwan has...") or as "I" if asked directly
"""

        return self._call_llm(system_prompt, query)
    
    def _demo_response(self, query: str) -> str:
        """Demo mode response with basic pattern matching."""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["experience", "work", "job", "career"]):
            return """**Work Experience** (Demo Mode)

Ikhwan has 4+ years of experience in data science:

- **BRI** (2022-Present): Data Scientist Junior Manager
  - Built NEXORA, a 5-agent enterprise chatbot
  - Created multi-agent code migration system (87% faster)
  - Graph-based recommender (22% conversion lift)

- **Waresix** (2021-2022): Junior Data Analyst
- **dibimbing.id** (2021): Data Science Instructor
- **ITB** (2019-2021): Research & Teaching Assistant

*For detailed answers, add your Groq API key.*
"""
        
        elif any(kw in query_lower for kw in ["skill", "tech", "stack", "language", "tool"]):
            return """**Technical Skills** (Demo Mode)

**AI & LLM:**
- Multi-Agent Systems, RAG, Agent Routing
- LLM: Qwen (self-hosted), Amazon Bedrock, GPT
- Tools: Kiro, Dataiku

**Graph AI:**
- Neo4j, TigerGraph, GNN, Knowledge Graphs

**Programming:**
- Python, SQL, PostgreSQL
- Spark, Cloudera, Confluent

*For detailed answers, add your Groq API key.*
"""
        
        elif any(kw in query_lower for kw in ["education", "degree", "university", "study"]):
            return """**Education** (Demo Mode)

**Institut Teknologi Bandung (ITB)**
- MSc Physics (2020-2021): GPA 3.92, Best Graduate
- BSc Physics (2016-2020): Dean's List 5 semesters

*For detailed answers, add your Groq API key.*
"""
        
        elif any(kw in query_lower for kw in ["award", "achievement", "recognition"]):
            return """**Awards** (Demo Mode)

- Employee of the Year, BRI (2025)
- Most Creative AI App, Confluent Hackathon (2025)
- Semifinalist, Bank Indonesia Hackathon (Top 30/2,336)
- Semifinalist, TrackAML Hackathon (2025)

*For detailed answers, add your Groq API key.*
"""
        
        elif any(kw in query_lower for kw in ["nexora", "chatbot", "agent"]):
            return """**NEXORA Project** (Demo Mode)

Enterprise data chatbot with 5 specialized agents:
1. Query Router - Intent classification
2. SQL Generator - Natural language to SQL
3. Data Validator - Business rules validation
4. Response Formatter - Output structuring
5. Feedback Handler - Continuous improvement

Tech: Amazon Bedrock, Dataiku, RAG
Serves 2,000+ data sources for 100+ users

*For detailed answers, add your Groq API key.*
"""
        
        else:
            return """**About Ikhwanul Muslimin** (Demo Mode)

Data Scientist at BRI specializing in AI agent systems. Built production multi-agent systems including NEXORA (5-agent chatbot) and code migration automation. 

Key highlights:
- 4+ years experience
- Employee of the Year 2025
- MSc Physics, ITB (GPA 3.92, Best Graduate)

Ask me about: experience, skills, education, awards, projects

*For detailed answers, add your Groq API key.*
"""
