import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from services.agent_orchestrator.graph import app # Import your compiled graph
from services.agent_orchestrator.state import AnalystState

async def run_test_simulation():
    print("Starting Swarm Simulation...")
    print("-----------------------------------")

    # 1. Define the initial state (Same as app.py)
    # We leave 'next_step' empty so memory_agent starts in 'Search' mode
    initial_state = {
        "question": "What was the revenue growth for Q3 2025 compared to industry benchmarks?",
        "user_id": "test_user_001",
        "iteration": 0,
        "next_step": "" 
    }

    print(f"User Question: {initial_state['question']}")
    print("-----------------------------------\n")

    # 2. Stream the graph execution
    # astream allows us to see every node as it completes
    try:
        async for output in app.astream(initial_state):
            for node_name, state_update in output.items():
                print(f"Node Finished: [{node_name.upper()}]")
                
                # Show what the node decided to do next
                if "next_step" in state_update:
                    print(f"   Routing to: {state_update['next_step']}")
                
                # Show if a report was generated
                if "full_report_text" in state_update:
                    report_preview = state_update['full_report_text'][:75].replace('\n', ' ')
                    print(f"   Report Sample: {report_preview}...")
                
                print("-" * 30)

    except Exception as e:
        print(f"Simulation Failed: {e}")

if __name__ == "__main__":
    # Run the async loop
    asyncio.run(run_test_simulation())
