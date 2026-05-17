from typing import Annotated, Any, Dict, List

from scheduler_mcp.models import JobRequest
from scheduler_mcp.transform.nl import parse_natural_language_job_request

FluxScriptResult = Annotated[
    Dict[str, Any],
    "Result of converting a JobRequest or natural-language request into a Flux batch script.",
]


def _coerce_job_request(job_request: Dict[str, Any]) -> JobRequest:
    return JobRequest(**job_request)


def _directive_lines(job_request: JobRequest) -> List[str]:
    lines = []
    if job_request.job_name:
        lines.append(f"# flux: --job-name={job_request.job_name}")
    lines.append(f"# flux: -N {job_request.num_nodes}")
    lines.append(f"# flux: -n {job_request.num_tasks}")
    lines.append(f"# flux: -c {job_request.cpus_per_task}")
    if job_request.gpus_per_task > 0:
        lines.append(f"# flux: -g {job_request.gpus_per_task}")
    if job_request.wall_time is not None:
        lines.append(f"# flux: -t {job_request.wall_time}s")
    return lines


def _command_line(job_request: JobRequest) -> str:
    output_file = job_request.output_file
    error_file = job_request.error_file

    if output_file and error_file:
        return f"{job_request.command} > {output_file} 2> {error_file}"
    if output_file:
        return f"{job_request.command} > {output_file}"
    if error_file:
        return f"{job_request.command} 2> {error_file}"
    return job_request.command


def _render_flux_batch_script(job_request: JobRequest) -> str:
    parts = ["#!/bin/bash", *_directive_lines(job_request), ""]
    if job_request.environment:
        for key, value in job_request.environment.items():
            parts.append(f"export {key}='{value}'")
        parts.append("")
    if job_request.working_directory:
        parts.append(f"cd {job_request.working_directory}")
        parts.append("")
    parts.append(_command_line(job_request))
    return "\n".join(parts)


def convert_job_request_to_flux_batch_script(
    job_request: Annotated[
        Dict[str, Any],
        "Structured job request to convert into a Flux batch script.",
    ],
) -> FluxScriptResult:
    """
    Convert a structured JobRequest into a minimal Flux batch script.
    """
    typed_job_request = _coerce_job_request(job_request)
    script = _render_flux_batch_script(typed_job_request)
    return {"success": True, "errors": [], "job_request": job_request, "script": script}


def convert_natural_language_job_request_to_flux_batch_script(
    text: Annotated[str, "Natural-language job request in Japanese."],
) -> FluxScriptResult:
    """
    Parse a natural-language request and convert it into a Flux batch script.
    """
    parse_result = parse_natural_language_job_request(text)
    if not parse_result["success"]:
        return {
            "success": False,
            "errors": parse_result["errors"],
            "job_request": None,
            "script": None,
        }

    job_request = parse_result["job_request"]
    return convert_job_request_to_flux_batch_script(job_request=job_request)
