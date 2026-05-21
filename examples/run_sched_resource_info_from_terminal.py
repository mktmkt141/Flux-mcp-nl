import asyncio
import json

from fastmcp import Client


async def main():
    job_id = input("scheduler jobid または jobid を入力してください: ").strip()
    if not job_id:
        print("入力が空です。")
        return

    async with Client("http://127.0.0.1:8090/mcp") as client:
        result = await client.call_tool(
            "flux_sched_resource_info",
            {"jobid": job_id},
        )
        print(json.dumps(result.data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
