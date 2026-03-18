from langchain_community.utilities import SQLDatabase
from ..state import AnalystState
import os

def schema_agent(state: AnalystState):
    """
    Connects to the local CockroachDB cluster and retrieves the schema.
    """
    print("🔍 Schema Agent: Inspecting CockroachDB cluster...")

    # Connection string for a local insecure CockroachDB node
    # Format: postgresql://<user>@<host>:<port>/<database>
    db_url = "cockroachdb://root@localhost:26270/analysis?sslmode=disable"
   
    try:
        # The engine args help stabilize the connection to Cockroach
        db = SQLDatabase.from_uri(
            db_url,
            engine_args={"pool_pre_ping": True}
        )
        schema_info = db.get_table_info()
        
        return {
            "schema_info": {"raw_schema": schema_info},
            "steps_completed": ["Retrieved CockroachDB Schema via Dialect"],
            "next_step": "sql_specialist"
        }
    except Exception as e:
        print(f"Connection Error: {e}")
        return {"next_step": "planner"}
