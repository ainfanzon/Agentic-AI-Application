from services.agent_orchestrator.state import AnalystState

def router(state: AnalystState):
    """
    Switchboard that converts Planner strings into actual Graph Node names.
    """
    plan = state.get("plan", [])
    current_step = state.get("next_step") # String set by the Planner

    # 1. SPECIAL CASE: Diagnostic Trigger
    if current_step == "diagnostic_check":
        return "diagnostic_agent"

    # 2. NODE MAPPING
    mapping = {
        "sql_specialist": "sql_specialist",
        "web_research": "web_research_agent", 
        "analysis_agent": "analysis_agent",
        "critic": "critic_agent"               
    }

    # 3. ROUTE SELECTION
    if current_step == "END":
        return "end"
        
    return mapping.get(current_step, current_step)
