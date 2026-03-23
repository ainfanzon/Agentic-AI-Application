from langgraph.graph import StateGraph, START, END
from services.agent_orchestrator.state import AnalystState
from services.agent_orchestrator.router import router

from services.agent_orchestrator.agents.planner import planner_agent
from services.agent_orchestrator.agents.diagnostic_agent import diagnostic_agent
from services.agent_orchestrator.agents.sql_specialist import sql_specialist
from services.agent_orchestrator.agents.web_research_agent import web_research_agent
from services.agent_orchestrator.agents.analysis_agent import analysis_agent
from services.agent_orchestrator.agents.critic import critic_agent
from services.agent_orchestrator.agents.memory_agent import memory_agent 

import networkx as nx
import matplotlib.pyplot as plt
import seaborn as sns

def visualize_compiled_graph(compiled_app):
    sns.set_theme(style="white")
    plt.figure(figsize=(12, 8))
    # ... [Your NetworkX drawing code here] ...
    plt.savefig("dynamic_swarm_graph.png")
    plt.show()

def create_swarm_graph():
    workflow = StateGraph(AnalystState)

    # 1. ADD NODES
    workflow.add_node("memory_agent", memory_agent)
    workflow.add_node("planner", planner_agent)
    workflow.add_node("diagnostic_agent", diagnostic_agent)
    workflow.add_node("sql_specialist", sql_specialist)
    workflow.add_node("web_research_agent", web_research_agent)
    workflow.add_node("analysis_agent", analysis_agent)
    workflow.add_node("critic_agent", critic_agent)

    # 2. ENTRY POINT
    workflow.set_entry_point("memory_agent")

    # 3. MEMORY AGENT ROUTING (Traffic Control)
    # If we just started, go to planner. If we just saved the final result, go to END.
    workflow.add_conditional_edges(
        "memory_agent",
        lambda x: "finish" if x.get("next_step") == "end" else "planner",
        {
            "planner": "planner",
            "finish": END
        }
    )

    # 4. THE DISPATCHER (Planner)
    workflow.add_conditional_edges(
        "planner",
        router,
        {
            "diagnostic_agent": "diagnostic_agent",
            "sql_specialist": "sql_specialist",
            "web_research_agent": "web_research_agent",
            "analysis_agent": "analysis_agent",
            "critic_agent": "critic_agent",
            "end": "memory_agent" 
        }
    )

    # 5. THE LINEAR PIPELINE
    workflow.add_edge("diagnostic_agent", "sql_specialist")
    workflow.add_edge("sql_specialist", "web_research_agent")
    workflow.add_edge("web_research_agent", "analysis_agent")
    workflow.add_edge("analysis_agent", "critic_agent")
    
    # 6. THE EXIT LOGIC (Critic)
    # Explicitly catch 'end' or 'END' and map them to memory_agent for consolidation
    workflow.add_conditional_edges(
        "critic_agent",
        lambda x: "memory_agent" if str(x.get("next_step")).lower() == "end" else "planner",
        {
            "memory_agent": "memory_agent",
            "planner": "planner"
        }
    )

    return workflow.compile()

app = create_swarm_graph()
