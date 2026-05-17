from fastmcp import FastMCP

from scheduler_mcp import __version__
from scheduler_mcp.registry import TOOLS


def create_server() -> FastMCP:
    server = FastMCP(
        name="Scheduler MCP",
        instructions="Scheduler-oriented MCP server with natural-language intake and Flux resource inspection.",
        version=__version__,
        on_duplicate="error",
    )
    for tool in TOOLS:
        server.add_tool(tool)
    return server

