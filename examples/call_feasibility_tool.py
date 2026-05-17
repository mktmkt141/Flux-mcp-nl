import asyncio

from fastmcp import Client


async def main():
    server = "http://127.0.0.1:8090/mcp"

    async with Client(server) as client:
        result = await client.call_tool(
            "check_job_request_feasibility",
            {
                "job_request": {
                    "command": "python train.py",
                    "num_nodes": 1,
                    "num_tasks": 1,
                    "cpus_per_task": 2,
                    "gpus_per_task": 0,
                    "wall_time": 3600,
                }
            },
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
