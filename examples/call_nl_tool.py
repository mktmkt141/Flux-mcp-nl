import asyncio

from fastmcp import Client


async def main():
    server = "http://127.0.0.1:8090/mcp"

    async with Client(server) as client:
        tools = await client.list_tools()
        print("=== tools ===")
        for tool in tools:
            print(tool.name)

        result = await client.call_tool(
            "parse_natural_language_job_request",
            {
                "text": "2ノード、各ノード4コアで1時間使って python train.py を実行したい"
            },
        )

        print("\n=== result ===")
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
