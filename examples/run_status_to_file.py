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
            "flux_get_job_info",
            {"job_id": job_id},
        )

    payload = {"job_id": job_id, "status_result": result.data}
    status_result = result.data
    info = status_result.get("info") or {}

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stem = f"{timestamp}-{job_id}-status"

    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    md_lines = [
        "# Flux job status",
        "",
        "## Input",
        "",
        f"- job_id: {job_id}",
        "",
        "## Summary",
        "",
        f"- success: {status_result.get('success')}",
        f"- status: {info.get('status')}",
        f"- result: {info.get('result')}",
        f"- returncode: {info.get('returncode')}",
        f"- runtime: {info.get('runtime')}",
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
