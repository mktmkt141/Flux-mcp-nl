import asyncio
import json

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
        parse_result = await client.call_tool(
            "parse_natural_language_job_request_with_gemini",
            {"text": text},
        )
        parse_data = parse_result.data
        print("=== Gemini parse result ===")
        print(json.dumps(parse_data, ensure_ascii=False, indent=2))

        if not parse_data.get("success"):
            return

        sched_result = await client.call_tool(
            "check_job_request_sched_feasibility",
            {"job_request": parse_data["job_request"]},
        )
        print("\n=== Scheduler feasibility ===")
        print(json.dumps(sched_result.data, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
