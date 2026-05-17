import asyncio
import sys

from fastmcp import Client


def _read_text() -> str:
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    return input("自然言語のジョブ要求を入力してください: ").strip()


async def main():
    text = _read_text()
    if not text:
        print("入力が空です。")
        return

    server = "http://127.0.0.1:8090/mcp"

    async with Client(server) as client:
        result = await client.call_tool(
            "submit_natural_language_job_request_to_flux_with_gemini",
            {"text": text},
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
