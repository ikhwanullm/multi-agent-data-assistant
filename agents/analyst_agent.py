"""Analyst Agent - Provides insights and analysis on data."""

from typing import Optional, List, Dict, Any
from .base import BaseAgent, AgentResponse
import config


class AnalystAgent(BaseAgent):
    """Analyzes data and provides insights."""
    
    def __init__(self):
        super().__init__(
            name="Analyst Agent",
            description="Provides data analysis and insights"
        )
    
    def process(self, query: str, context: dict = None) -> AgentResponse:
        """Analyze data and provide insights."""
        
        # Get data from context (from SQL agent results)
        data = context.get("data", []) if context else []
        sql = context.get("sql", "") if context else ""
        
        # Generate analysis
        analysis = self._generate_analysis(query, data, sql)
        
        return AgentResponse(
            success=True,
            message=analysis,
            data={"query": query, "data_points": len(data)},
            agent_name=self.name
        )
    
    def _generate_analysis(self, query: str, data: List[Dict], sql: str) -> str:
        """Generate analysis from data."""
        
        if config.DEMO_MODE or (not self.groq_client and not self.openai_client):
            return self._demo_analysis(query, data)
        
        # Prepare data summary for LLM
        data_summary = self._summarize_data(data)
        
        system_prompt = """You are a data analyst. Analyze the provided data and give insights.

Guidelines:
1. Be specific and actionable
2. Highlight key patterns or anomalies
3. Suggest potential next steps
4. Keep response concise (2-3 paragraphs)"""

        user_message = f"""User Question: {query}

SQL Query Used: {sql}

Data Summary:
{data_summary}

Provide analysis and insights."""

        return self._call_llm(system_prompt, user_message)
    
    def _demo_analysis(self, query: str, data: List[Dict]) -> str:
        """Demo mode analysis."""
        if not data:
            return """📊 **Analysis** (Demo Mode)

No data provided for analysis. Try running a data query first, then ask for insights.

**Example workflow:**
1. "Show me top 10 customers by spending"
2. "What insights can you give from this data?"
"""
        
        # Basic statistical analysis
        num_records = len(data)
        
        # Try to find numeric columns
        numeric_cols = []
        if data:
            for key, value in data[0].items():
                if isinstance(value, (int, float)):
                    numeric_cols.append(key)
        
        analysis = f"""📊 **Analysis** (Demo Mode)

**Data Overview:**
- Total records: {num_records}
- Numeric columns found: {', '.join(numeric_cols) if numeric_cols else 'None'}

**Key Observations:**
1. The dataset contains {num_records} records for analysis
2. {'Multiple numeric fields available for quantitative analysis' if numeric_cols else 'Consider requesting data with numeric fields for deeper analysis'}

**Recommendations:**
- For spending analysis, look at total_amount and quantity fields
- Consider segmenting by customer or time period for trends
- Compare against historical data for growth patterns

*Note: This is a demo analysis. With API key, you'll get AI-powered insights.*
"""
        return analysis
    
    def _summarize_data(self, data: List[Dict], max_rows: int = 10) -> str:
        """Create text summary of data for LLM."""
        if not data:
            return "No data available"
        
        summary_lines = []
        summary_lines.append(f"Total records: {len(data)}")
        summary_lines.append(f"Columns: {', '.join(data[0].keys())}")
        summary_lines.append("\nSample data (first {max_rows} rows):")
        
        for i, row in enumerate(data[:max_rows]):
            summary_lines.append(str(row))
        
        return "\n".join(summary_lines)
