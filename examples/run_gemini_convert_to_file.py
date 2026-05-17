import asyncio
import json
from datetime import datetime
from pathlib import Path

from fastmcp import Client


def _sanitize_text(text: str) -> str:
    return text.encode("utf-16", "surrogatepass").decode("utf-16", "replace")


def _slugify(text: str) -> str:
    cleaned = "".join(ch if ch.isalnum() else "-" for ch in text.lower())
    cleaned = "-".join(part for part in cleaned.split("-") if part)
    return cleaned[:40] or "job-request"


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
        convert_result = await client.call_tool(
            "convert_natural_language_job_request_to_flux_batch_script",
            {"text": text},
        )

    payload = {
        "input": text,
        "parse_result": parse_result.data,
        "convert_result": convert_result.data,
    }

    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stem = f"{timestamp}-{_slugify(text)}-convert"

    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    job_request = parse_result.data.get("job_request")
    script = convert_result.data.get("script")

    md_lines = [
        "# Gemini conversion result",
        "",
        "## Input",
        "",
        text,
        "",
        "## JobRequest",
        "",
        "```json",
        json.dumps(job_request, ensure_ascii=False, indent=2),
        "```",
        "",
        "## Flux script",
        "",
        "```bash",
        script or "",
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
