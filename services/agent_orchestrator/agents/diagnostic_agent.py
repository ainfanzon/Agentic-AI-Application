from services.mcp_host import call_cockroach_mcp
from services.agent_orchestrator.state import AnalystState

async def diagnostic_agent(state: AnalystState):
    print("Diagnostic Agent: Running Deep Health Check via MCP...")
    
    try:
        # 1. Check general cluster health
        status = await call_cockroach_mcp("get_cluster_status", {"detailed": False})
        
        # 2. Check for slow queries to help the SQL Specialist optimize
        slow_queries = await call_cockroach_mcp("get_slow_queries", {"limit": 3})
        
        report = f"""
        --- DATABASE HEALTH REPORT ---
        CLUSTER STATUS: {status}
        RECENT SLOW QUERIES: {slow_queries}
        ------------------------------
        """
        
        # Add the report to the context so the SQL Specialist can see it
        current_context = state.get("data_context", [])
        
        return {
            "data_context": current_context + [report],
            "next_step": "sql_specialist" # Hand off to the SQL expert
        }

    except Exception as e:
        print(f"AICA: Diagnostic Agent Failed: {e}")
        # If diagnostics fail, don't stop the swarm, just move to SQL
        return {"next_step": "sql_specialist"}
