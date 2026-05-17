import asyncio

from fastmcp import Client


def _sanitize_text(text: str) -> str:
    return text.encode("utf-16", "surrogatepass").decode("utf-16", "replace")


async def main():
    text = input("自然言語のジョブ要求を入力してください: ").strip()
    if not text:
        print("入力が空です。")
        return

    text = _sanitize_text(text)

    async with Client("http://127.0.0.1:8090/mcp") as client:
        result = await client.call_tool(
            "parse_natural_language_job_request_with_gemini",
            {"text": text},
        )
        print(result)


if __name__ == "__main__":
    asyncio.run(main())
