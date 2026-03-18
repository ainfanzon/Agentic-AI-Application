from ..state import AnalystState

def router(state: AnalystState):
    """
    Determines the next agent to call based on the 'plan' 
    and the 'next_step' values in the state.
    """
    plan = state.get("plan", [])
    current_step = state.get("next_step")

    print(f"🚦 Router: Current step is '{current_step}'. Evaluating next move...")

    # 1. Check if we have a valid plan
    if not plan:
        print("🛑 Router Warning: Plan is empty. Routing to Critic for final check.")
        return "critic"

    # 2. Handle the "Self-Healing" Diagnostic Step
    if current_step == "diagnostic_check":
        return "diagnostic_agent"

    # 3. Handle Standard Specialist Mapping
    # This map ensures that LLM-generated strings match your node names
    mapping = {
        "sql_specialist": "sql_specialist",
        "sql_agent": "sql_specialist",
        "web_research": "web_research",
        "web_research_agent": "web_research",
        "analysis_agent": "analysis_agent",
        "data_analysis": "analysis_agent",
        "critic": "critic",
        "critic_agent": "critic"
    }

    # 4. Determine the return value
    # If the current_step is in our map, return the internal node name
    next_node = mapping.get(current_step, current_step)
    
    print(f"⏩ Router: Routing to node '{next_node}'")
    return next_node
