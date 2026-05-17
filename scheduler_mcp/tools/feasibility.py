from typing import Annotated, Any, Dict, List, Optional

from scheduler_mcp.models import JobRequest
from scheduler_mcp.tools.resource import get_flux_resource_list

FeasibilityResult = Annotated[
    Dict[str, Any],
    "Result of comparing a JobRequest against currently free Flux resources.",
]


def _coerce_job_request(job_request: Dict[str, Any]) -> JobRequest:
    return JobRequest(**job_request)


def _collect_reasons(job_request: JobRequest, free: Dict[str, Any]) -> List[str]:
    reasons: List[str] = []
    requested_cores = job_request.num_tasks * job_request.cpus_per_task

    if job_request.num_nodes > free["nodes"]:
        reasons.append(
            f"Requested {job_request.num_nodes} nodes, but only {free['nodes']} free nodes are available."
        )
    if requested_cores > free["cores"]:
        reasons.append(
            f"Requested {requested_cores} total CPU cores, but only {free['cores']} free cores are available."
        )
    if job_request.gpus_per_task > free["gpus"]:
        reasons.append(
            f"Requested {job_request.gpus_per_task} GPUs per task, but only {free['gpus']} free GPUs are available."
        )

    return reasons


def check_job_request_feasibility(
    job_request: Annotated[
        Dict[str, Any],
        "Structured job request to compare against current free Flux resources.",
    ],
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> FeasibilityResult:
    """
    Report whether a JobRequest appears schedulable now using a simple free-resource comparison.
    """
    typed_job_request = _coerce_job_request(job_request)
    resource_report = get_flux_resource_list(uri=uri)
    free = resource_report["free"]
    reasons = _collect_reasons(typed_job_request, free)

    return {
        "schedulable_now": not reasons,
        "reasons": reasons,
        "requested": {
            "nodes": typed_job_request.num_nodes,
            "tasks": typed_job_request.num_tasks,
            "cores": typed_job_request.num_tasks * typed_job_request.cpus_per_task,
            "gpus_per_task": typed_job_request.gpus_per_task,
            "wall_time": typed_job_request.wall_time,
            "command": typed_job_request.command,
        },
        "available": free,
    }
