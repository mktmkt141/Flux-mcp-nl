from typing import Annotated, Any, Dict, Optional

from scheduler_mcp.analysis.feasibility import check_job_request_feasibility
from scheduler_mcp.sched.feasibility import check_job_request_sched_feasibility

from .info import (
    flux_sched_resource_get_property,
    flux_sched_resource_remove_property,
    flux_sched_resource_set_property,
    flux_sched_resource_set_status,
    flux_sched_resource_status,
)

SchedulerHelperResult = Annotated[
    Dict[str, Any],
    "Helper result that stitches multiple scheduler-side checks into one report.",
]


def flux_sched_verify_resource_property_roundtrip(
    resource_path: Annotated[str, "The resource vertex path to tag temporarily."],
    key: Annotated[str, "The property key to set, read back, and remove."],
    value: Annotated[str, "The temporary property value to verify."],
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerHelperResult:
    key_val = f"{key}={value}"
    set_result = flux_sched_resource_set_property(resource_path, key_val, uri=uri)
    if not set_result["success"]:
        return {
            "success": False,
            "error": set_result["error"],
            "resource_path": resource_path,
            "key": key,
            "value": value,
            "steps": {
                "set_property": set_result,
                "get_property_after_set": None,
                "remove_property": None,
                "get_property_after_remove": None,
            },
            "verified": False,
        }

    get_after_set = flux_sched_resource_get_property(resource_path, key, uri=uri)
    remove_result = flux_sched_resource_remove_property(resource_path, key, uri=uri)
    get_after_remove = flux_sched_resource_get_property(resource_path, key, uri=uri)

    verified = (
        get_after_set["success"]
        and value in get_after_set.get("result", {}).get("values", [])
        and remove_result["success"]
        and not get_after_remove["success"]
    )

    return {
        "success": True,
        "error": None,
        "resource_path": resource_path,
        "key": key,
        "value": value,
        "steps": {
            "set_property": set_result,
            "get_property_after_set": get_after_set,
            "remove_property": remove_result,
            "get_property_after_remove": get_after_remove,
        },
        "verified": verified,
    }


def flux_sched_verify_resource_status_roundtrip(
    resource_path: Annotated[str, "The resource vertex path to toggle temporarily."],
    temporary_status: Annotated[str, "The temporary status to apply during the check."] = "down",
    restore_status: Annotated[str, "The status to restore after the temporary change."] = "up",
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerHelperResult:
    before_status = flux_sched_resource_status(uri=uri)
    set_temporary = flux_sched_resource_set_status(resource_path, temporary_status, uri=uri)
    during_status = flux_sched_resource_status(uri=uri)
    restore_result = flux_sched_resource_set_status(resource_path, restore_status, uri=uri)
    after_status = flux_sched_resource_status(uri=uri)

    return {
        "success": set_temporary["success"] and restore_result["success"],
        "error": set_temporary["error"] or restore_result["error"],
        "resource_path": resource_path,
        "temporary_status": temporary_status,
        "restore_status": restore_status,
        "steps": {
            "before_status": before_status,
            "set_temporary_status": set_temporary,
            "during_status": during_status,
            "restore_status": restore_result,
            "after_status": after_status,
        },
    }


def assess_job_request_submission_readiness(
    job_request: Annotated[
        Dict[str, Any],
        "Structured job request to compare across job-side and scheduler-side readiness checks.",
    ],
    uri: Annotated[Optional[str], "The Flux connection URI. Defaults to the local instance."] = None,
) -> SchedulerHelperResult:
    direct_feasibility = check_job_request_feasibility(job_request, uri=uri)
    scheduler_feasibility = check_job_request_sched_feasibility(job_request, uri=uri)

    if not scheduler_feasibility["success"]:
        recommendation = "inspect_scheduler"
        rationale = "The scheduler-side feasibility RPC failed, so the request needs investigation before submit."
    elif scheduler_feasibility.get("satisfiable") is False:
        recommendation = "adjust_request"
        rationale = "The scheduler reports that the request cannot be satisfied by the current cluster graph."
    elif direct_feasibility["schedulable_now"]:
        recommendation = "submit_now"
        rationale = "Both the scheduler-side and free-resource checks indicate that the request can run now."
    else:
        recommendation = "wait_or_reduce_request"
        rationale = (
            "The scheduler says the request is satisfiable overall, but the current free-resource check says it is not runnable now."
        )

    return {
        "success": scheduler_feasibility["success"],
        "error": scheduler_feasibility["error"],
        "job_request": job_request,
        "direct_feasibility": direct_feasibility,
        "scheduler_feasibility": scheduler_feasibility,
        "recommendation": recommendation,
        "rationale": rationale,
    }


def summarize_sched_verification_scenarios() -> SchedulerHelperResult:
    scenarios = [
        {
            "name": "feasibility",
            "input_example": "1 node, 1 task, 1 core, short wall time",
            "success_markers": ["success=true", "satisfiable=true"],
        },
        {
            "name": "allocation",
            "input_example": "1 node, 1 task, 1 core",
            "success_markers": ["allocation.status=ALLOCATED", "allocation.R_summary.nodelist"],
        },
        {
            "name": "reserve",
            "input_example": "same request while resources are already allocated",
            "success_markers": ["allocation.status=RESERVED"],
        },
        {
            "name": "release",
            "input_example": "cancel a scheduler allocation jobid",
            "success_markers": ["success=true", "resource_info becomes null afterwards"],
        },
        {
            "name": "resource_status",
            "input_example": "call with no arguments",
            "success_markers": ["success=true", "resource_status.all"],
        },
        {
            "name": "resource_find",
            "input_example": "criteria=status=up",
            "success_markers": ["success=true", "resource_find.R"],
        },
        {
            "name": "property_roundtrip",
            "input_example": "resource_path=/cluster0/<node>, key=group, value=verify",
            "success_markers": ["verified=true", "get_property_after_set.result.values contains verify"],
        },
        {
            "name": "status_roundtrip",
            "input_example": "resource_path=/cluster0/<node>/core0",
            "success_markers": ["success=true", "set_temporary_status.success=true", "restore_status.success=true"],
        },
    ]

    return {"success": True, "error": None, "scenarios": scenarios}
