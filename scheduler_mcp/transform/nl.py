import re
from typing import Annotated, Any, Dict, List, Optional

from scheduler_mcp.models import JobRequest

ParseJobRequestResult = Annotated[
    Dict[str, Any],
    "Result of parsing a natural-language job request into a structured JobRequest.",
]


def _parse_duration_seconds(text: str) -> Optional[int]:
    hours_match = re.search(r"(\d+)時間", text)
    minutes_match = re.search(r"(\d+)分", text)
    hours = int(hours_match.group(1)) if hours_match else 0
    minutes = int(minutes_match.group(1)) if minutes_match else 0
    seconds = hours * 3600 + minutes * 60
    return seconds or None


def _extract_first_int(patterns: List[str], text: str, default: int) -> int:
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return int(match.group(1))
    return default


def _extract_command(text: str) -> Optional[str]:
    patterns = [
        r"以内に\s+(.+?)\s+を実行したい",
        r"以内に\s+(.+?)\s+を流したい",
        r"以内に\s+(.+?)\s+を走らせたい",
        r"使って\s+(.+?)\s+を実行したい",
        r"使って\s+(.+?)\s+を流したい",
        r"使って\s+(.+?)\s+を走らせたい",
        r"(python\s+.+)$",
        r"([A-Za-z0-9_./-]+\s+.+)$",
        r"([A-Za-z0-9_./-]+)$",
    ]
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1).strip()
    return None


def parse_natural_language_job_request(
    text: Annotated[str, "Natural-language job request in Japanese."],
) -> ParseJobRequestResult:
    """
    Parse a constrained Japanese natural-language job request into a minimal JobRequest.
    """
    normalized = " ".join(text.strip().split())
    errors: List[str] = []

    command = _extract_command(normalized)
    if not command:
        errors.append("Could not extract command from the input text.")

    num_nodes = _extract_first_int([r"(\d+)ノード"], normalized, 1)
    num_tasks = _extract_first_int([r"(\d+)タスク"], normalized, 1)
    cpus_per_task = _extract_first_int([r"各ノード(\d+)コア", r"(\d+)コア"], normalized, 1)
    gpus_per_task = _extract_first_int([r"GPUを(\d+)枚", r"GPU(\d+)枚"], normalized, 0)
    wall_time = _parse_duration_seconds(normalized)

    if errors:
        return {"success": False, "errors": errors, "job_request": None}

    job_request = JobRequest(
        command=command,
        num_nodes=num_nodes,
        num_tasks=num_tasks,
        cpus_per_task=cpus_per_task,
        gpus_per_task=gpus_per_task,
        wall_time=wall_time,
    )
    return {"success": True, "errors": [], "job_request": job_request.to_dict()}
