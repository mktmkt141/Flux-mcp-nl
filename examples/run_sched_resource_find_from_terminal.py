import asyncio
import json

from fastmcp import Client


async def main():
    criteria = input("criteria を入力してください (例: status=up): ").strip()
    if not criteria:
        print("入力が空です。")
        return

    find_format = input("format を入力してください (空なら未指定): ").strip() or None

    async with Client("http://127.0.0.1:8090/mcp") as client:
        result = await client.call_tool(
            "flux_sched_resource_find",
            {"criteria": criteria, "find_format": find_format},
        )
        print(json.dumps(result.data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
