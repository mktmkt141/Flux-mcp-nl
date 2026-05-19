import asyncio

from fastmcp import Client


async def main():
    job_id = input("cancelするjob_idを入力してください: ").strip()
    if not job_id:
        print("job_idが空です。")
        return

    async with Client("http://127.0.0.1:8090/mcp") as client:
        result = await client.call_tool("flux_cancel_job", {"job_id": job_id})
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
