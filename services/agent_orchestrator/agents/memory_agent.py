import uuid
import json
from services.mcp_host import call_cockroach_mcp
from services.agent_orchestrator.state import AnalystState

async def memory_agent(state: AnalystState):
    """
    Manages Long-Term Memory (LTM) by interacting with CockroachDB.
    Acts as the entry gateway and the final exit gate.
    """
    
    # Identify if we are at the START or the END of the workflow
    is_final_save = state.get("next_step") == "end"

    # --- ROLE 1: RETRIEVAL (Start of Graph) ---
    if not is_final_save:
        print("🧠 Memory Agent: Fetching relevant Long-Term Memory...")
        
        question = state.get("question", "")
        # Search for 'revenue' if present, otherwise broaden to 'insight'
        search_term = "revenue" if "revenue" in question.lower() else "insight"
        
        try:
            # Search both key and value columns
            query = f"""
                SELECT memory_value 
                FROM swarm_memory 
                WHERE memory_value ILIKE '%{search_term}%' 
                OR memory_key ILIKE '%{search_term}%' 
                LIMIT 5
            """
            memories = await call_cockroach_mcp("execute_query", {"query": query})
            
            # Debugging line to see the JSON structure returned by MCP
            print(f"DEBUG MCP: {memories}")

            memory_list = []
            
            # --- THE UNSTOPPABLE PARSER ---
            if isinstance(memories, dict):
                # 1. Try to get rows from the dict keys
                rows = memories.get("rows") or memories.get("result") or []
                
                # 2. Fallback: If 'formatted_result' exists and rows is empty, parse the string
                if not rows and memories.get("formatted_result"):
                    try:
                        rows = json.loads(memories["formatted_result"])
                    except:
                        pass

                # 3. Extract the memory_value from the identified rows
                if isinstance(rows, list):
                    for row in rows:
                        if isinstance(row, dict) and "memory_value" in row:
                            memory_list.append(row["memory_value"])
                        elif isinstance(row, str):
                            # In case it returns a list of raw strings
                            memory_list.append(row)

            # 4. Fallback for raw list response
            elif isinstance(memories, list):
                memory_list = [
                    row.get("memory_value") if isinstance(row, dict) else str(row) 
                    for row in memories
                ]

            if memory_list:
                print(f"✅ Found {len(memory_list)} relevant past insights.")
            else:
                print(f"ℹ️ Query executed, but no memories matched '{search_term}' in the response structure.")

            return {
                "memory_context": "\n".join(memory_list) if memory_list else "No previous memory found.",
                "next_step": "planner" 
            }
        except Exception as e:
            print(f"⚠️ Memory Retrieval Failed: {e}")
            return {"memory_context": "Error loading memory.", "next_step": "planner"}

    # --- ROLE 2: CONSOLIDATION (End of Graph) ---
    else:
        print("🧠 Memory Agent: Consolidating new insights into LTM...")
        
        critique = state.get("critique", "")
        final_answer = state.get("plan", []) 

        if critique or final_answer:
            try:
                mem_key = f"insight_{uuid.uuid4().hex[:8]}"
                new_insight = f"User asked: {state.get('question')}. Result: {str(final_answer)[:200]}"
                
                insert_query = f"""
                INSERT INTO swarm_memory (user_id, memory_key, memory_value, importance)
                VALUES ('default', '{mem_key}', '{new_insight.replace("'", "''")}', 5)
                """
                
                await call_cockroach_mcp("execute_query", {"query": insert_query})
                print(f"💾 Final state consolidated and saved with key: {mem_key}")
            except Exception as e:
                print(f"⚠️ Memory Consolidation Failed: {e}")

        return {"next_step": "end"}
