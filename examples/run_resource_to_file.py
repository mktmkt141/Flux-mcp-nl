import asyncio
import json
from datetime import datetime
from pathlib import Path

from fastmcp import Client


async def main():
    async with Client("http://127.0.0.1:8090/mcp") as client:
        result = await client.call_tool("get_flux_resource_list", {})

    payload = result.data
    output_dir = Path("outputs")
    output_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    stem = f"{timestamp}-flux-resource-list"

    json_path = output_dir / f"{stem}.json"
    md_path = output_dir / f"{stem}.md"

    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    free = payload.get("free", {})
    up = payload.get("up", {})

    md_lines = [
        "# Flux resource list",
        "",
        "## Summary",
        "",
        f"- Free nodes: {free.get('nodes')}",
        f"- Free cores: {free.get('cores')}",
        f"- Free gpus: {free.get('gpus')}",
        f"- Up nodes: {up.get('nodes')}",
        f"- Up cores: {up.get('cores')}",
        f"- Up gpus: {up.get('gpus')}",
        "",
        "## Output",
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
