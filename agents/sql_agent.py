"""SQL Agent - Generates and executes SQL queries from natural language."""

import re
import sqlite3
from typing import Optional, List, Dict, Any
from .base import BaseAgent, AgentResponse
import config


class SQLAgent(BaseAgent):
    """Converts natural language to SQL and executes queries."""
    
    SCHEMA_INFO = """
Database Schema:
- customers (id, name, email, city, created_at)
- products (id, name, category, price, stock)
- orders (id, customer_id, product_id, quantity, total_amount, order_date, status)

Relationships:
- orders.customer_id -> customers.id
- orders.product_id -> products.id
"""
    
    def __init__(self):
        super().__init__(
            name="SQL Agent",
            description="Generates SQL queries from natural language"
        )
        self.db_path = config.DATABASE_PATH
    
    def process(self, query: str, context: dict = None) -> AgentResponse:
        """Convert query to SQL and execute."""
        
        # Generate SQL
        sql = self._generate_sql(query)
        
        if not sql:
            return AgentResponse(
                success=False,
                message="Could not generate SQL for this query",
                agent_name=self.name
            )
        
        # Validate SQL (basic safety check)
        if not self._is_safe_sql(sql):
            return AgentResponse(
                success=False,
                message="Query contains unsafe operations",
                agent_name=self.name
            )
        
        # Execute SQL
        results, error = self._execute_sql(sql)
        
        if error:
            return AgentResponse(
                success=False,
                message=f"SQL Error: {error}",
                data={"sql": sql},
                agent_name=self.name
            )
        
        return AgentResponse(
            success=True,
            message=f"Found {len(results)} results",
            data={"sql": sql, "results": results},
            agent_name=self.name
        )
    
    def _generate_sql(self, query: str) -> Optional[str]:
        """Generate SQL from natural language."""
        
        if config.DEMO_MODE or (not self.groq_client and not self.openai_client):
            return self._pattern_based_sql(query)
        
        # LLM-based generation
        system_prompt = f"""You are a SQL expert. Convert the user's question to a SQLite query.

{self.SCHEMA_INFO}

Rules:
1. Only generate SELECT queries (read-only)
2. Use proper JOINs when needed
3. Limit results to {config.MAX_SQL_RESULTS} rows
4. Return ONLY the SQL query, no explanations

Example:
User: Show top 5 customers by spending
SQL: SELECT c.name, SUM(o.total_amount) as total_spent 
     FROM customers c 
     JOIN orders o ON c.id = o.customer_id 
     GROUP BY c.id 
     ORDER BY total_spent DESC 
     LIMIT 5"""

        result = self._call_llm(system_prompt, query)
        
        # Extract SQL from response
        sql = self._extract_sql(result)
        return sql
    
    def _pattern_based_sql(self, query: str) -> Optional[str]:
        """Simple pattern matching for demo mode."""
        query_lower = query.lower()
        
        patterns = [
            # Top customers by spending
            (r"top (\d+) customers?.*(spend|amount|order)", 
             lambda m: f"""SELECT c.name, c.email, SUM(o.total_amount) as total_spent 
                          FROM customers c 
                          JOIN orders o ON c.id = o.customer_id 
                          GROUP BY c.id 
                          ORDER BY total_spent DESC 
                          LIMIT {m.group(1)}"""),
            
            # Count customers
            (r"(how many|count) customers?",
             lambda m: "SELECT COUNT(*) as customer_count FROM customers"),
            
            # List products
            (r"(list|show|all) products?",
             lambda m: "SELECT * FROM products LIMIT 20"),
            
            # Products by category
            (r"products?.*(category|in) (\w+)",
             lambda m: f"SELECT * FROM products WHERE category LIKE '%{m.group(2)}%'"),
            
            # Recent orders
            (r"(recent|latest|last) (\d+)? ?orders?",
             lambda m: f"SELECT * FROM orders ORDER BY order_date DESC LIMIT {m.group(2) or 10}"),
            
            # Total revenue/sales
            (r"total (revenue|sales|amount)",
             lambda m: "SELECT SUM(total_amount) as total_revenue FROM orders"),
            
            # Orders by status
            (r"orders?.*(status|pending|completed|shipped)",
             lambda m: "SELECT status, COUNT(*) as count FROM orders GROUP BY status"),
            
            # Default - list customers
            (r"customers?",
             lambda m: "SELECT * FROM customers LIMIT 20"),
        ]
        
        for pattern, sql_func in patterns:
            match = re.search(pattern, query_lower)
            if match:
                return sql_func(match)
        
        # Fallback
        return "SELECT * FROM customers LIMIT 10"
    
    def _extract_sql(self, text: str) -> Optional[str]:
        """Extract SQL query from LLM response."""
        # Remove markdown code blocks if present
        text = re.sub(r'```sql\s*', '', text)
        text = re.sub(r'```\s*', '', text)
        
        # Find SELECT statement
        match = re.search(r'(SELECT.*?)(?:;|$)', text, re.IGNORECASE | re.DOTALL)
        if match:
            return match.group(1).strip()
        return text.strip()
    
    def _is_safe_sql(self, sql: str) -> bool:
        """Basic SQL injection prevention."""
        dangerous = ['DROP', 'DELETE', 'UPDATE', 'INSERT', 'ALTER', 'CREATE', '--', ';']
        sql_upper = sql.upper()
        
        for keyword in dangerous:
            if keyword in sql_upper and keyword != 'SELECT':
                # Allow these only in specific contexts
                if keyword in ['UPDATE', 'DELETE', 'INSERT', 'DROP', 'ALTER', 'CREATE']:
                    return False
        return True
    
    def _execute_sql(self, sql: str) -> tuple[List[Dict[str, Any]], Optional[str]]:
        """Execute SQL query and return results."""
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            
            cursor.execute(sql)
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            results = [dict(row) for row in rows]
            
            conn.close()
            return results[:config.MAX_SQL_RESULTS], None
            
        except sqlite3.Error as e:
            return [], str(e)
        except Exception as e:
            return [], str(e)
