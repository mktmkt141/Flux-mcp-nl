from typing import Annotated, Any, Dict, Optional, Union

SchedulerInfoResult = Annotated[
    Dict[str, Any],
    "Result of asking the Flux scheduler for internal queue or resource metadata.",
]


def _get_handle(uri: Optional[str] = None):
    import flux

    if uri:
        return flux.Flux(uri)
    return flux.Flux()


def flux_sched_qmanager_stats(
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> SchedulerInfoResult:
    """
    Retrieve queue-manager statistics from the Flux scheduler.
    """
    try:
        handle = _get_handle(uri)
        stats = handle.rpc("sched-fluxion-qmanager.stats-get").get()
        return {
            "success": True,
            "error": None,
            "stats": stats,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "stats": None,
        }


def flux_sched_resource_info(
    jobid: Annotated[
        Union[int, str],
        "The scheduler job identifier to inspect.",
    ],
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> SchedulerInfoResult:
    """
    Retrieve scheduler-side resource metadata for a specific job.
    """
    try:
        import flux.job

        handle = _get_handle(uri)
        resource_info = handle.rpc(
            "sched-fluxion-resource.info",
            {"jobid": flux.job.JobID(jobid)},
        ).get()
        return {
            "success": True,
            "error": None,
            "jobid": str(jobid),
            "resource_info": resource_info,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "jobid": str(jobid),
            "resource_info": None,
        }


def flux_sched_resource_status(
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> SchedulerInfoResult:
    """
    Retrieve scheduler-side resource status grouped by categories such as up/down/allocated.
    """
    try:
        handle = _get_handle(uri)
        resource_status = handle.rpc("sched-fluxion-resource.status").get()
        return {
            "success": True,
            "error": None,
            "resource_status": resource_status,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "resource_status": None,
        }


def flux_sched_resource_find(
    criteria: Annotated[
        str,
        "A scheduler-side resource query such as 'status=up'.",
    ],
    find_format: Annotated[
        Optional[str],
        "Optional output format such as 'json'.",
    ] = None,
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> SchedulerInfoResult:
    """
    Search the scheduler resource graph for vertices that match the given criteria.
    """
    try:
        handle = _get_handle(uri)
        payload = {"criteria": criteria}
        if find_format:
            payload["format"] = find_format
        resource_find = handle.rpc("sched-fluxion-resource.find", payload).get()
        return {
            "success": True,
            "error": None,
            "criteria": criteria,
            "find_format": find_format,
            "resource_find": resource_find,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "criteria": criteria,
            "find_format": find_format,
            "resource_find": None,
        }
