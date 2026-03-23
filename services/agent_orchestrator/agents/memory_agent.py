import uuid
import json
import asyncio
from services.agent_orchestrator.state import AnalystState
from services.memory_service.vector_search import VectorMemory

# Initialize the Vector Service
# This handles model loading and CockroachDB vector formatting
memory_service = VectorMemory()

async def memory_agent(state: AnalystState):
    """
    Manages Long-Term Memory (LTM) using Vector Similarity Search.
    Professional Version: Handles high-quality report persistence and retrieval.
    """
    
    user_id = state.get("user_id", "default")
    # In LangGraph, we detect the 'end' signal to switch from 'Search' to 'Save'
    is_final_save = str(state.get("next_step", "")).lower() == "end"

    # --- ROLE 1: SEMANTIC RETRIEVAL (Start of Graph) ---
    if not is_final_save:
        print("Memory Agent: Performing Semantic Search in LTM...")
        # Use 'question' as the primary search query
        question = state.get("question", "")
        memory_list = []
        
        try:
            # The vector service finds conceptually similar past insights
            memories = memory_service.search(user_id, question, limit=5)
            
            for row in memories:
                # row structure: (memory_key, memory_value, similarity_score)
                _, val, score, *rest = row
                # We only include memories that are actually relevant (> 0.35 similarity)

                try:
                    # Ensure score is a float for the comparison
                    if isinstance(score, (int, float, str)):
                        numeric_score = float(score) 
                    else:
                        continue
        
                    if numeric_score > 0.50:  # Lowered to 0.50 to catch that 60.2% match
                        memory_list.append(val)
                        jjj
                except (ValueError, TypeError):
                    print(f"DEBUG: Skipping row due to invalid score format: {score}")

            # We return the context to the planner so it can avoid repeating work
            return {
                "memory_context": memory_list if memory_list else ["No previous insights found."],
                "next_step": "planner" 
            }
        except Exception as e:
            print(f"AICA: Vector Retrieval Failed: {e}")
            return {"memory_context": [f"Memory error: {str(e)}"], "next_step": "planner"}
    
    # --- ROLE 2: SEMANTIC CONSOLIDATION (End of Graph) ---
    else:
        # 1. Get the high-quality report (Checking both possible keys)
        full_report = state.get("full_report_text") or state.get("analysis_results")
        
        # 2. Get the original question to use as the UNIQUE KEY
        question = state.get("question", "").strip()

        # DEBUG: Verify state content
        print(f"DEBUG: Memory Agent State Check - Report length: {len(full_report) if full_report else 0}")

        if full_report and question:
            print(f"Memory Agent: Finalizing persistence for: '{question[:30]}...'")
            try:
                # --- FIX: Define the missing variables ---
                mem_key = question
                summary_insight = f"Analysis for: {question} | Summary: {full_report[:200].replace('\n', ' ')}..."
                
                # 3. Hand off to Vector Service
                await memory_service.add_memory(
                    user_id=user_id, 
                    key=mem_key, 
                    value=summary_insight,
                    full_report_text=full_report
                )
                
                print(f"Professional Sync: Insight vectorized and saved with key: {mem_key[:20]}...")
            except Exception as e:
                print(f"AICA: Memory Consolidation Failed: {e}")
        else:
            print("Memory Agent: No report found to save. Skipping consolidation.")

        # 4. Signal LangGraph to reach the END node
        return {"next_step": "end"}
