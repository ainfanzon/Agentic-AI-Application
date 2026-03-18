import asyncio
import uuid
from services.agent_orchestrator.agents.memory_agent import memory_agent

async def run_sanity_check():
    print("🚀 Starting Memory Agent Sanity Check...")

    # --- TEST 1: RETRIEVAL MODE ---
    # We simulate the START of a graph run
    start_state = {
        "question": "What is our current revenue?",
        "next_step": None, # Not 'end', so it should trigger Retrieval
        "iteration": 0
    }
    
    print("\n--- Testing Retrieval (Start of Flow) ---")
    retrieval_result = await memory_agent(start_state)
    
    if "memory_context" in retrieval_result:
        print(f"✅ Retrieval Success!")
        print(f"   Context Found: {retrieval_result['memory_context'][:100]}...")
    else:
        print("❌ Retrieval failed to return memory_context.")

    # --- TEST 2: CONSOLIDATION MODE ---
    # We simulate the END of a graph run
    end_state = {
        "question": "What is our current revenue?",
        "next_step": "end", # This triggers the Save logic
        "plan": ["Revenue is looking good at $50k"],
        "critique": "The data is accurate.",
        "iteration": 1
    }

    print("\n--- Testing Consolidation (End of Flow) ---")
    consolidation_result = await memory_agent(end_state)

    if consolidation_result.get("next_step") == "end":
        print("✅ Consolidation Logic completed.")
        print("   Check your CockroachDB table 'swarm_memory' for a new row!")
    else:
        print("❌ Consolidation failed to signal 'end'.")

if __name__ == "__main__":
    asyncio.run(run_sanity_check())
