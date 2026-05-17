import asyncio

from fastmcp import Client


async def main():
    server = "http://127.0.0.1:8090/mcp"

    async with Client(server) as client:
        result = await client.call_tool(
            "flux_get_job_logs",
            {
                "job_id": "ƒMGs3Nhm",
            },
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
