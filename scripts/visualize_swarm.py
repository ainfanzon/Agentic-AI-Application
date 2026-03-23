import asyncio
import sys
import os

# 1. FIX PATHING
current_dir = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(current_dir)
sys.path.append(ROOT_DIR)

# 2. IMPORTS
try:
    # We must use HumanMessage objects to satisfy the 'add' operator in your state
    from langchain_core.messages import HumanMessage, BaseMessage
    from services.agent_orchestrator.graph import app, visualize_compiled_graph
    print("✅ Successfully connected to the Agentic Swarm Graph.")
except ImportError as e:
    print(f"❌ Import Error: {e}")
    sys.exit(1)

async def run_live_monitor(user_query):
    """Executes the swarm with live terminal telemetry."""
    
    # --- Part A: Diagram Generation ---
    print("\n🎨 Generating Architecture Diagram...")
    visualize_compiled_graph(app)

    # --- Part B: Live Monitor ---
    print(f"\n{'='*60}")
    print(f"🚀 SWARM LIVE MONITOR: {user_query}")
    print(f"{'='*60}")

    # FIX: Initialize messages as a LIST of objects, matching app.py Section 7
    initial_state = {
        "question": user_query,
        "analysis_results": "",
        "messages": [HumanMessage(content=user_query)]
    }
    
    try:
        # astream allows us to see the nodes firing in real-time
        async for output in app.astream(initial_state):
            for node_name, state_update in output.items():
                print(f"\n🔄 [ACTIVE NODE]: {node_name.upper()}")
                
                # Check for message updates
                if "messages" in state_update:
                    new_msgs = state_update["messages"]
                    # Extract content regardless of if it's a list or single object
                    if isinstance(new_msgs, list) and len(new_msgs) > 0:
                        last_msg = new_msgs[-1]
                        content = getattr(last_msg, 'content', str(last_msg))
                        print(f"   ∟ 💬 Output: {content[:100]}...")

                if "next_step" in state_update:
                    print(f"   ∟ ➡️ Routing: {state_update['next_step'].upper()}")

                print(f"✅ [COMPLETED]: {node_name.upper()}")
                print("-" * 30)

    except Exception as e:
        print(f"❌ Swarm Execution Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_prompt = "What was the revenue growth for Q3 2025 compared to industry benchmarks?"
    asyncio.run(run_live_monitor(test_prompt))
