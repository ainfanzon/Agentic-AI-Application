import re
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from services.mcp_host import call_cockroach_mcp
from services.agent_orchestrator.state import AnalystState

async def sql_specialist(state: AnalystState):
    """
    Writes and executes CockroachDB-compatible SQL using the native MCP toolset.
    """
    print("🐝 SQL Specialist: Crafting and Executing Query via MCP...")

    llm = ChatOllama(model="llama3", temperature=0)

    # 1. DYNAMIC SCHEMA FETCH
    schema_raw = await call_cockroach_mcp("describe_table", {"table_name": "revenue"})
    
    # Escape curly braces so LangChain doesn't mistake JSON for input variables
    schema_safe = str(schema_raw).replace("{", "{{").replace("}", "}}")

    system_prompt = f"""You are a precise CockroachDB SQL Expert. 
    Output ONLY the raw SQL query. No explanation, no markdown backticks, no introduction.
    
    CRITICAL RULES:
    1. TABLE: Only query the 'revenue' table.
    2. SELECTION: Always select 'month' and 'amount'.
    3. FORMATTING: Use TO_CHAR(month, 'YYYY-MM-DD') AS month_str.
    4. FILTER: Use (month >= CURRENT_DATE - INTERVAL '6 months').
    5. ORDER: Always ORDER BY month ASC.
    6. FORBIDDEN: Do NOT use DATE_SUB or DATE_ADD.
    7. TERMINATION: Always end the query with a semicolon (;).
    
    SCHEMA:
    {schema_safe}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", f"Question: {state['question']}")
    ])

    # 2. GENERATE SQL
    response = (prompt | llm).invoke({}).content.strip()

    # 3. CLEANUP & REGEX SAFETY NET
    sql_match = re.search(r"(SELECT.*?;)", response, re.DOTALL | re.IGNORECASE)
    clean_query = sql_match.group(1) if sql_match else response
    clean_query = clean_query.replace("```sql", "").replace("```", "").strip()

    # Standardize INTERVAL syntax for CockroachDB
    if "DATE_SUB" in clean_query:
        clean_query = re.sub(r"DATE_SUB\((.*?), INTERVAL (\d+) MONTH\)", r"\1 - INTERVAL '\2 months'", clean_query, flags=re.IGNORECASE)
    clean_query = re.sub(r"INTERVAL (\d+) MONTH", r"INTERVAL '\1 months'", clean_query, flags=re.IGNORECASE)

    try:
        print(f"📡 MCP Executing: {clean_query}")
        result = await call_cockroach_mcp("execute_query", {"query": clean_query})
        
        # Log the full result for verification
        print(f"DEBUG: SQL Results: {result}") 
        
        # --- THE MERGED FIX ---
        # Returning [result] as a list triggers the 'add' operator in state.py
        # This appends the data to the memory instead of overwriting it.
        return {
            "current_sql": clean_query,
            "data_context": [result], 
            "next_step": "web_research"
        }
    except Exception as e:
        print(f"❌ SQL Execution Error: {e}")
        return {
            "critique": f"SQL Syntax Error: {str(e)}", 
            "next_step": "planner"
        }
