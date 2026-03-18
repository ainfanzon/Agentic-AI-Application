# test_swarm.py
import sys
import os

# Ensure the script can find the 'services' directory
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.agent_orchestrator.graph import app

def run_scenario(name, state):
    print(f"\n{'='*20}")
    print(f"SCENARIO: {name}")
    print(f"{'='*20}")
    
    # We use .stream to see each node as it activates
    for event in app.stream(state):
        for node_name, output in event.items():
            print(f"\n📍 Node executed: {node_name}")
            
            # Print the next step chosen by the node
            if "next_step" in output:
                print(f"   ➡️  Next Step: {output['next_step']}")
            
            # Print the plan if the planner generated one
            if "plan" in output:
                print(f"   📝 Plan: {output['plan']}")
            
            # Print if the planner flagged a memory resolution
            if "is_resolved_by_memory" in output:
                print(f"   🧠 Memory Match found: {output['is_resolved_by_memory']}")

# --- SCENARIO 1: The Short-Circuit ---
# Testing if the Planner sees the answer in memory and stops immediately.
short_circuit_state = {
    "question": "What was our revenue in Q3?",
    "memory_context": "Past Insight: Q3 revenue was $1.2M based on last week's analysis.",
    "iteration": 0,
    "data_context": []
}

# --- SCENARIO 2: The Augmented Plan ---
# Testing if the Planner skips SQL (since revenue is known) but keeps Web Research.
augmented_plan_state = {
    "question": "Compare our Q3 revenue to industry benchmarks.",
    "memory_context": "Past Insight: Q3 revenue was $1.2M.",
    "iteration": 0,
    "data_context": []
}

if __name__ == "__main__":
    # Execute Scenario 1
    run_scenario("Short-Circuit (Memory Hit)", short_circuit_state)
    
    print("\n\n")
    
    # Execute Scenario 2
    run_scenario("Augmented Plan (Partial Memory)", augmented_plan_state)
