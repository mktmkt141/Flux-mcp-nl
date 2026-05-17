import asyncio
import json
from datetime import datetime
from pathlib import Path

from fastmcp import Client


async def main():
    job_id = input("確認したい job_id を入力してください: ").strip()
    if not job_id:
        print("job_id が空です。")
        return

    async with Client("http://127.0.0.1:8090/mcp") as client:
        result = await client.call_tool(
            "flux_get_job_logs",
            {"job_id": job_id},
        )

    payload = {"job_id": job_id, "logs_result": result.data}
    logs_result = result.data

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stem = f"{timestamp}-{job_id}-logs"

    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = logs_result.get("lines") or []
    md_lines = [
        "# Flux job logs",
        "",
        "## Input",
        "",
        f"- job_id: {job_id}",
        "",
        "## Summary",
        "",
        f"- success: {logs_result.get('success')}",
        f"- complete: {logs_result.get('complete')}",
        f"- return_code: {logs_result.get('return_code')}",
        "",
        "## Output lines",
        "",
        "```text",
        "".join(lines),
        "```",
        "",
        "## Full output",
        "",
        "```json",
        json.dumps(payload, ensure_ascii=False, indent=2),
        "```",
        "",
    ]
    md_path.write_text("\n".join(md_lines), encoding="utf-8")

    print(f"JSON saved to: {json_path}")
    print(f"Markdown saved to: {md_path}")
    print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
