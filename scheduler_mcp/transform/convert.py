from typing import Annotated, Any, Dict, List

from scheduler_mcp.models import JobRequest
from scheduler_mcp.transform.nl import parse_natural_language_job_request

FluxScriptResult = Annotated[
    Dict[str, Any],
    "Result of converting a JobRequest or natural-language request into a Flux batch script.",
]
FluxJobspecResult = Annotated[
    Dict[str, Any],
    "Result of converting a JobRequest into a Flux jobspec dictionary.",
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


def _fallback_flux_jobspec(job_request: JobRequest) -> Dict[str, Any]:
    command = ["/bin/bash", "-lc", job_request.command]
    system: Dict[str, Any] = {}
    if job_request.job_name:
        system["job"] = {"name": job_request.job_name}
    if job_request.wall_time is not None:
        system["duration"] = job_request.wall_time
    if job_request.working_directory:
        system["cwd"] = job_request.working_directory
    if job_request.environment:
        system["environment"] = job_request.environment
    if job_request.output_file:
        system["output"] = job_request.output_file
    if job_request.error_file:
        system["error"] = job_request.error_file

    slot_children: List[Dict[str, Any]] = [
        {"type": "core", "count": job_request.cpus_per_task}
    ]
    if job_request.gpus_per_task > 0:
        slot_children.append({"type": "gpu", "count": job_request.gpus_per_task})

    resources = [
        {
            "type": "node",
            "count": job_request.num_nodes,
            "with": [
                {
                    "type": "slot",
                    "label": "task",
                    "count": job_request.num_tasks,
                    "with": slot_children,
                }
            ],
        }
    ]

    return {
        "version": 1,
        "resources": resources,
        "tasks": [{"command": command, "slot": "task", "count": {"per_slot": 1}}],
        "attributes": {"system": system},
    }


def _jobspec_from_flux_api(job_request: JobRequest) -> Dict[str, Any]:
    import flux.job

    command = ["/bin/bash", "-lc", job_request.command]
    jobspec = flux.job.JobspecV1.from_command(
        command=command,
        num_tasks=job_request.num_tasks,
        cores_per_task=job_request.cpus_per_task,
        gpus_per_task=job_request.gpus_per_task or None,
        num_nodes=job_request.num_nodes,
    )

    if job_request.environment:
        jobspec.environment = job_request.environment
    if job_request.wall_time is not None:
        jobspec.duration = job_request.wall_time
    if job_request.working_directory is not None:
        jobspec.cwd = job_request.working_directory
    if job_request.output_file is not None:
        jobspec.output = job_request.output_file
    if job_request.error_file is not None:
        jobspec.error = job_request.error_file
    if job_request.job_name is not None:
        jobspec.name = job_request.job_name

    try:
        return jobspec.jobspec
    except AttributeError:
        return _fallback_flux_jobspec(job_request)


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


def convert_job_request_to_flux_jobspec(
    job_request: Annotated[
        Dict[str, Any],
        "Structured job request to convert into a Flux jobspec dictionary.",
    ],
) -> FluxJobspecResult:
    """
    Convert a structured JobRequest into a minimal Flux jobspec dictionary.
    """
    typed_job_request = _coerce_job_request(job_request)
    errors: List[str] = []

    try:
        jobspec = _jobspec_from_flux_api(typed_job_request)
    except Exception as exc:
        jobspec = _fallback_flux_jobspec(typed_job_request)
        errors.append(
            f"Flux Python API was unavailable or failed; returned fallback jobspec instead. Detail: {exc}"
        )

    return {
        "success": True,
        "errors": errors,
        "job_request": job_request,
        "jobspec": jobspec,
    }
