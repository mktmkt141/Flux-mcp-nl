import json
from typing import Annotated, Any, Dict, Optional

from scheduler_mcp.models import JobRequest
from scheduler_mcp.transform.convert import convert_job_request_to_flux_jobspec

SchedulerAllocationResult = Annotated[
    Dict[str, Any],
    "Result of asking the Flux scheduler to allocate resources for a jobspec.",
]


def _get_handle(uri: Optional[str] = None):
    import flux

    if uri:
        return flux.Flux(uri)
    return flux.Flux()


def _dump_job_request(job_request: JobRequest) -> Dict[str, Any]:
    if hasattr(job_request, "model_dump"):
        return job_request.model_dump()
    if hasattr(job_request, "dict"):
        return job_request.dict()
    if hasattr(job_request, "to_dict"):
        return job_request.to_dict()
    return dict(job_request.__dict__)


def flux_sched_resource_allocate_with_satisfiability(
    jobspec_dict: Annotated[
        Dict[str, Any],
        "A Flux jobspec dictionary to allocate with the scheduler.",
    ],
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> SchedulerAllocationResult:
    """
    Ask the Flux scheduler to allocate resources immediately, or report satisfiability.
    """
    try:
        import flux.job

        handle = _get_handle(uri)
        jobid = flux.job.JobID(handle.rpc("sched-fluxion-resource.next_jobid").get()["jobid"])
        payload = {
            "cmd": "allocate_with_satisfiability",
            "jobid": jobid,
            "jobspec": json.dumps(jobspec_dict),
        }
        allocation = handle.rpc("sched-fluxion-resource.match", payload).get()
        return {
            "success": True,
            "error": None,
            "jobspec": jobspec_dict,
            "allocation": allocation,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "jobspec": jobspec_dict,
            "allocation": None,
        }


def check_job_request_sched_allocate(
    job_request: Annotated[
        Dict[str, Any],
        "Structured job request to convert into a Flux jobspec before scheduler allocation.",
    ],
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> SchedulerAllocationResult:
    """
    Convert a JobRequest into a Flux jobspec and ask the scheduler to allocate resources.
    """
    typed_job_request = JobRequest(**job_request)
    dumped_job_request = _dump_job_request(typed_job_request)
    jobspec_result = convert_job_request_to_flux_jobspec(job_request=dumped_job_request)

    if not jobspec_result["success"]:
        return {
            "success": False,
            "error": "; ".join(jobspec_result["errors"]) or "jobspec conversion failed",
            "job_request": dumped_job_request,
            "jobspec": None,
            "allocation": None,
        }

    allocation_result = flux_sched_resource_allocate_with_satisfiability(
        jobspec_dict=jobspec_result["jobspec"],
        uri=uri,
    )

    return {
        "success": allocation_result["success"],
        "error": allocation_result["error"],
        "job_request": dumped_job_request,
        "jobspec": allocation_result["jobspec"],
        "allocation": allocation_result["allocation"],
        "conversion_errors": jobspec_result["errors"],
    }
