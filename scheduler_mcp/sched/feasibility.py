from typing import Annotated, Any, Dict, Optional

from scheduler_mcp.models import JobRequest
from scheduler_mcp.transform.convert import convert_job_request_to_flux_jobspec

SchedulerFeasibilityResult = Annotated[
    Dict[str, Any],
    "Result of asking the Flux scheduler whether a jobspec is theoretically feasible.",
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


def flux_sched_resource_feasibility_check(
    jobspec_dict: Annotated[
        Dict[str, Any],
        "A Flux jobspec dictionary to check with the scheduler.",
    ],
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> SchedulerFeasibilityResult:
    """
    Ask the Flux scheduler whether a jobspec is theoretically satisfiable.
    """
    try:
        handle = _get_handle(uri)
        # In this Flux RPC, a satisfiable request returns no payload (Python None / JSON null).
        # We convert that "silent success" into an explicit satisfiable=True result for MCP clients.
        raw_response = handle.rpc("feasibility.check", {"jobspec": jobspec_dict}).get()
        return {
            "success": True,
            "error": None,
            "jobspec": jobspec_dict,
            "satisfiable": True,
            "scheduler_message": None,
            "feasibility": {
                "satisfiable": True,
                "raw_response": raw_response,
            },
        }
    except OSError as exc:
        # Flux reports an impossible request by raising OSError("Unsatisfiable request").
        # That is a scheduler verdict, so expose it as satisfiable=False instead of success=False.
        if "Unsatisfiable request" in str(exc):
            return {
                "success": True,
                "error": None,
                "jobspec": jobspec_dict,
                "satisfiable": False,
                "scheduler_message": str(exc),
                "feasibility": {
                    "satisfiable": False,
                    "raw_response": None,
                },
            }
        return {
            "success": False,
            "error": str(exc),
            "jobspec": jobspec_dict,
            "satisfiable": None,
            "scheduler_message": None,
            "feasibility": None,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "jobspec": jobspec_dict,
            "satisfiable": None,
            "scheduler_message": None,
            "feasibility": None,
        }


def check_job_request_sched_feasibility(
    job_request: Annotated[
        Dict[str, Any],
        "Structured job request to convert into a Flux jobspec before scheduler feasibility check.",
    ],
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> SchedulerFeasibilityResult:
    """
    Convert a JobRequest into a Flux jobspec and ask the scheduler for feasibility.
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
            "feasibility": None,
        }

    feasibility_result = flux_sched_resource_feasibility_check(
        jobspec_dict=jobspec_result["jobspec"],
        uri=uri,
    )

    return {
        "success": feasibility_result["success"],
        "error": feasibility_result["error"],
        "job_request": dumped_job_request,
        "jobspec": feasibility_result["jobspec"],
        "satisfiable": feasibility_result["satisfiable"],
        "scheduler_message": feasibility_result["scheduler_message"],
        "feasibility": feasibility_result["feasibility"],
        "conversion_errors": jobspec_result["errors"],
    }
