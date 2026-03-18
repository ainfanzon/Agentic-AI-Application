from typing import Annotated, List, TypedDict, Dict, Any
from operator import add

class AnalystState(TypedDict):
    """
    The 'Shared Whiteboard' for the Autonomous Analyst swarm.
    Using Annotated[list, add] ensures data from different agents 
    is appended, not overwritten.
    """
    # 1. Input & Context
    question: str
    plan: List[str]
    strategy: str                       

    # 2. The Accumulative Memory
    # CRITICAL: This allows the SQL result AND the Web result to coexist.
    data_context: Annotated[List[Any], add]

    # 3. Execution Data
    schema_info: Dict[str, Any]         
    current_sql: str
    analysis_results: str

    # 4. Control Flow
    iteration: int
    critique: str
    next_step: str

    # 5. Output Artifacts (Paths to generated charts/PDFs)
    artifacts: Annotated[List[str], add]

    # 6. Holds relevant LTM insights for the current session
    memory_context: List[str]  
