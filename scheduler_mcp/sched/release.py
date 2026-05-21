from typing import Annotated, Any, Dict, Optional, Union

SchedulerReleaseResult = Annotated[
    Dict[str, Any],
    "Result of releasing scheduler-side allocated or reserved resources.",
]


def _get_handle(uri: Optional[str] = None):
    import flux

    if uri:
        return flux.Flux(uri)
    return flux.Flux()


def flux_sched_resource_cancel(
    jobid: Annotated[
        Union[int, str],
        "The scheduler job identifier to release resources for.",
    ],
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> SchedulerReleaseResult:
    """
    Cancel a scheduler-side allocation or reservation and return its resources to the free pool.
    """
    try:
        import flux.job

        handle = _get_handle(uri)
        result = handle.rpc(
            "sched-fluxion-resource.cancel",
            {"jobid": flux.job.JobID(jobid)},
        ).get()
        return {
            "success": True,
            "error": None,
            "jobid": str(jobid),
            "result": result,
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "jobid": str(jobid),
            "result": None,
        }
