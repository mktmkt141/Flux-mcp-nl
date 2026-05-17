from typing import Annotated, Any, Dict, Optional, Union

JobActionResult = Annotated[
    Dict[str, Any],
    "Structured response for Flux job cancellation requests.",
]


def flux_cancel_job(
    job_id: Annotated[Union[int, str], "Flux job identifier."],
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> JobActionResult:
    """
    Request cancellation of a specific Flux job.
    """
    try:
        import flux
        import flux.job

        handle = flux.Flux(uri) if uri else flux.Flux()
        flux_job_id = flux.job.JobID(job_id)
        flux.job.cancel(handle, flux_job_id)
        return {
            "success": True,
            "error": None,
            "message": f"Job {job_id} cancellation requested.",
            "job_id": str(job_id),
        }
    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "message": "Cancellation had an error.",
            "job_id": str(job_id),
        }
