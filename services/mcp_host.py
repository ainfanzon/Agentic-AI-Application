import os
import asyncio
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

load_dotenv()

COCKROACH_URL = os.getenv("DATABASE_URL")

server_params = StdioServerParameters(
    command="uvx",
    args=[
        "--from", "git+https://github.com/amineelkouhen/mcp-cockroachdb.git",
        "cockroachdb-mcp-server",
        "--url", COCKROACH_URL
    ],
    env=os.environ.copy()
)

async def call_cockroach_mcp(tool_name: str, arguments: dict):
    """
    Verified Native Tools:
    - execute_query: {"query": "SELECT ..."}
    - get_cluster_status: {"detailed": true}
    - describe_table: {"table_name": "revenue"}
    - list_tables: {"db_schema": "public"}
    """
    print(f"🐝 Native Cockroach MCP: Executing '{tool_name}'...")
    
    try:
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                response = await session.call_tool(tool_name, arguments)
                
                if hasattr(response, 'content') and response.content:
                    return response.content[0].text
                return str(response)
                    
    except Exception as e:
        return f"Error: {str(e)}"
