import asyncio

from fastmcp import Client


async def main():
    server = "http://127.0.0.1:8090/mcp"

    async with Client(server) as client:
        result = await client.call_tool(
            "convert_natural_language_job_request_to_flux_batch_script",
            {
                "text": "1ノードで30分使って hostname を実行したい",
            },
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
