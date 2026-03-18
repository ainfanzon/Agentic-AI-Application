from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from services.agent_orchestrator.state import AnalystState

def critic_agent(state: AnalystState):
    print("⚖️ Critic Agent: Finalizing report and evaluating findings...")
    
    # --- LOOP PREVENTION ---
    iteration = state.get("iteration", 0)
    
    llm = ChatOllama(model="llama3", temperature=0)
    
    # 1. Retrieve data
    data = state.get("data_context", [])
    analysis = state.get("analysis_results", "")
    
    # 2. CRITICAL FIX: Escape curly braces in the data
    safe_data = str(data).replace("{", "{{").replace("}", "}}")
    safe_analysis = str(analysis).replace("{", "{{").replace("}", "}}")

    system_prompt = """You are a Senior Business Analyst. 
    Review the data and analysis provided. 
    
    TASKS:
    1. Provide a concise executive summary of the revenue trends.
    2. Compare the internal data with the industry benchmarks provided.
    3. If a 'DATABASE HEALTH REPORT' is present in the context, mention any performance 
       observations (e.g., cluster status or slow queries) as a technical footnote.
    
    End your response with 'FINAL REPORT COMPLETE'."""

    # 3. Use the safe strings in the prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", f"Data context: {safe_data}\n\nAnalysis Summary: {safe_analysis}")
    ])

    try:
        # Check if we are already looping too much
        if iteration >= 3:
            print("⚠️ Max iterations reached. Forcing final report generation.")
            footer = "\n\n**Note:** This report was finalized after multiple iterations to ensure availability."
        else:
            footer = ""

        response = (prompt | llm).invoke({}).content + footer
        
        print("\n--- FINAL EXECUTIVE SUMMARY ---")
        print(response)
        print("----------------------------------\n")

        # Use "end" (lowercase) to match the routing key in graph.py
        return {
            "analysis_results": response,
            "next_step": "end"
        }
    except Exception as e:
        print(f"⚠️ Critic Agent failed: {e}")
        # Even on failure, we want to go to memory_agent to end gracefully
        return {"next_step": "end", "critique": str(e)}
