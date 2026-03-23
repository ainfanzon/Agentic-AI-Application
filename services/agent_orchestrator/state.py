from typing import Annotated, List, TypedDict, Dict, Any
from operator import add

class AnalystState(TypedDict):
    """
    The 'Shared Whiteboard' for the Autonomous Analyst swarm.
    """
    # 1. Input & Context
    question: str
    user_id: str # Added for multi-user support
    plan: List[str]
    strategy: str                       

    # 2. The Accumulative Memory
    # This allows SQL and Web results to coexist.
    data_context: Annotated[List[Any], add]

    # 3. Execution Data
    schema_info: Dict[str, Any]         
    current_sql: str
    analysis_results: str

    # --- THE CRITICAL FIX ---
    # This stores the finalized, high-quality summary for the database.
    full_report_text: str 

    # 4. Control Flow
    iteration: int
    critique: str
    next_step: str

    # 5. Output Artifacts
    artifacts: Annotated[List[str], add]

    # 6. LTM Context
    # Using Annotated[List, add] here is safer if you retrieve memory in stages.
    memory_context: Annotated[List[str], add]
