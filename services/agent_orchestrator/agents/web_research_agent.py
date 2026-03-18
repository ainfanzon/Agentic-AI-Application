import os
from langchain_tavily import TavilySearch
from services.agent_orchestrator.state import AnalystState

def web_research_agent(state: AnalystState):
    print("🌐 Web Research Agent: Searching for industry benchmarks...")
    
    # Use the 2026-standard Tavily tool to stop the deprecation warnings
    search = TavilySearch(max_results=3)
    query = f"SaaS industry revenue growth benchmarks 2025-2026"

    try:
        results = search.run(query)
        
        # We return ONLY the new finding in a list. 
        # LangGraph's 'operator.add' in state.py appends this to the SQL rows.
        new_finding = f"WEB RESEARCH FINDINGS: {results}"
        
        return {
            "data_context": [new_finding],
            "next_step": "analysis_agent"
        }
    except Exception as e:
        print(f"⚠️ Web Research Failed: {e}")
        # Return an empty list to satisfy the 'add' reducer without crashing the state
        return {
            "data_context": [], 
            "next_step": "analysis_agent"
        }
