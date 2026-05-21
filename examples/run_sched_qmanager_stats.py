import asyncio
import json

from fastmcp import Client


async def main():
    async with Client("http://127.0.0.1:8090/mcp") as client:
        result = await client.call_tool("flux_sched_qmanager_stats", {})
        print(json.dumps(result.data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
