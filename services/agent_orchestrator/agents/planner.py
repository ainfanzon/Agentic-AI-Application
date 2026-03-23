from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List
from services.agent_orchestrator.state import AnalystState

# --- Schema Definitions ---
class Step(BaseModel):
    step: str = Field(description="The name of the agent or action (e.g., 'diagnostic_agent', 'sql_specialist')")
    description: str = Field(description="Details of what needs to be done")

class AnalysisPlan(BaseModel):
    steps: List[Step] = Field(description="A list of sequential steps")
    strategy: str = Field(description="DB_PATH | WEB_PATH | HYBRID_PATH")
    is_resolved_by_memory: bool = Field(description="True if the 'Past Insights' already answer the user's question completely.")

def planner_agent(state: AnalystState):
    # 1. Setup State & Inputs
    question = state.get("question", state.get("input", "")).lower()
    iteration = state.get("iteration", 0)
    data_context = state.get("data_context", [])
    past_memory = state.get("memory_context", "No previous memory found.")

    print(f"Planner: Orchestrating swarm with Memory Context (Iteration {iteration})...")

    # 2. Hardcoded Diagnostic Logic
    is_slow_request = any(word in question for word in ["slow", "lag", "unresponsive", "down", "performance"])
    has_run_diagnostics = any("DATABASE HEALTH REPORT" in str(item) for item in data_context)
    needs_diagnostics = (is_slow_request or iteration > 0) and not has_run_diagnostics

    # 3. LLM Setup (Memory-Aware)
    llm = ChatOllama(model="llama3", temperature=0, format="json")
    parser = PydanticOutputParser(pydantic_object=AnalysisPlan)

    system_prompt = """You are the Lead Planner for an Autonomous Analytics Swarm.
    Decompose the user question into a step-by-step plan using Past Insights to avoid redundancy.

    ### MEMORY & CONTEXT
    Use 'Past Insights' to:
    1. Avoid redundant steps already performed in previous sessions.
    2. Use specific SQL tables/filters discovered previously.
    3. If the 'Past Insights' fully answer the question, set is_resolved_by_memory to True.

    AVAILABLE SPECIALISTS:
    - diagnostic_agent: Use ONLY for database performance issues.
    - sql_specialist: Query CockroachDB for internal revenue data.
    - web_research: Search for external industry benchmarks.
    - analysis_agent: Compare data and generate insights.
    - critic: Finalize and check for hallucinations.

    {format_instructions}
    """

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", "PAST INSIGHTS:\n{past_memory}\n\nCURRENT QUESTION:\n{question}")
    ])

    # 4. Invoke LLM
    chain = prompt | llm | parser
    result = chain.invoke({
        "question": question, 
        "past_memory": past_memory,
        "format_instructions": parser.get_format_instructions()
    })

    # 5. Merge Strategy & Steps
    final_steps = []
    
    # If memory already has the answer, short-circuit to end
    if result.is_resolved_by_memory:
        print("Memory Match: Question resolved by past insights.")
        return {"next_step": "end", "iteration": iteration + 1}

    if needs_diagnostics:
        final_steps.append("diagnostic_agent")

    # Standardize step names from LLM
    llm_steps = [s.step.lower().replace(" ", "_") for s in result.steps]
    
    # Combine, avoiding duplicate diagnostics
    for s in llm_steps:
        if s not in final_steps:
            final_steps.append(s)

    if not final_steps:
        final_steps = ["critic"]

    return {
        "plan": final_steps,
        "strategy": result.strategy,
        "next_step": final_steps[0],
        "iteration": iteration + 1
    }
