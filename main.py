import os
import asyncio
import subprocess
from dotenv import load_dotenv
from services.agent_orchestrator.graph import app

# 1. Load environment variables (TAVILY_API_KEY, etc.)
load_dotenv()

async def run_test():
    # 2. Fully initialize the Shared State
    initial_state = {
        "question": "Show me a revenue trend for the last 6 months and compare it with industry benchmarks from the web.",
        "plan": [],
        "strategy": "HYBRID_PATH", # Explicitly tell the router we want DB + WEB
        "data_context": [],
        "schema_info": {},         # Initialize to avoid NoneType errors
        "iteration": 0,
        "artifacts": [],
        "analysis_results": ""
    }

    print("\n--- Starting Autonomous Analyst Swarm ---")

    # 3. Execute the Graph
    async for output in app.astream(initial_state):
        for node_name, state_update in output.items():
            print(f"\n[Node: {node_name}]")

            # Show Planner output
            if "plan" in state_update and state_update["plan"]:
                print("Generated Plan:")
                for i, step in enumerate(state_update["plan"], 1):
                    print(f"  {i}. {step}")

            # Show Router decisions
            if "next_step" in state_update:
                print(f"Routing decision: {state_update['next_step']}")

    print("\n--- Swarm Execution Complete ---")

    # 4. AUTO-DISPLAY ARTIFACTS
    # This will open the revenue_trend.png using the default macOS Preview app
    chart_path = "artifacts/revenue_trend.png"
    if os.path.exists(chart_path):
        print(f"Opening visualization: {chart_path}")
        try:
            # 'open' is the macOS command to open a file with its default app
            subprocess.run(["open", chart_path], check=True)
        except Exception as e:
            print(f"Could not open chart automatically: {e}")

if __name__ == "__main__":
    asyncio.run(run_test())
