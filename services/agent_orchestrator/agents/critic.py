from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from services.agent_orchestrator.state import AnalystState

# 1. Change to async def for professional consistency with memory_agent
async def critic_agent(state: AnalystState):
    print("Critic Agent: Finalizing report and evaluating findings...")
    
    iteration = state.get("iteration", 0)
    llm = ChatOllama(model="llama3", temperature=0)
    
    data = state.get("data_context", [])
    analysis = state.get("analysis_results", "")
    
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

    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human", f"Data context: {safe_data}\n\nAnalysis Summary: {safe_analysis}")
    ])

    try:
        if iteration >= 3:
            print("Max iterations reached. Forcing final report generation.")
            footer = "\n\n**Note:** This report was finalized after multiple iterations to ensure availability."
        else:
            footer = ""

        # Use ainvoke for async execution
        response_obj = await (prompt | llm).ainvoke({})
        response = response_obj.content + footer
        
        print("\n--- FINAL EXECUTIVE SUMMARY ---")
        print(response)
        print("----------------------------------\n")

        # CRITICAL: This return dictionary UPDATES the AnalystState
        return {
            "analysis_results": response,
            "full_report_text": response, # This MUST match state.py
            "next_step": "end"
        }

    except Exception as e:
        print(f"AICA: Critic Agent failed: {e}")
        return {
            "next_step": "end", 
            "critique": str(e),
            "full_report_text": f"Error during generation: {str(e)}"
        }
