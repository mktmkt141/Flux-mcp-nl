import asyncio
import json

from fastmcp import Client


BAD_SCRIPT = """#!/bin/bash
# flux -N 1
# flux: -t 30m

"""


async def main():
    async with Client("http://127.0.0.1:8090/mcp") as client:
        result = await client.call_tool(
            "validate_flux_batch_script",
            {"script": BAD_SCRIPT},
        )
        print("=== Input script ===")
        print(BAD_SCRIPT)
        print("=== Validate result ===")
        print(json.dumps(result.data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
