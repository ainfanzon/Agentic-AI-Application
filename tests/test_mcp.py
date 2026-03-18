import asyncio
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
from dotenv import load_dotenv

load_dotenv()

async def discover_tools():
    server_params = StdioServerParameters(
        command="uvx",
        args=[
            "--from", "git+https://github.com/amineelkouhen/mcp-cockroachdb.git",
            "cockroachdb-mcp-server",
            "--url", os.getenv("DATABASE_URL")
        ]
    )
    
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            # This is the magic command to see what is actually available
            tools = await session.list_tools()
            print("\n🛠️ AVAILABLE TOOLS ON THIS SERVER:")
            for tool in tools.tools:
                print(f"- {tool.name}: {tool.description}")

if __name__ == "__main__":
    asyncio.run(discover_tools())
