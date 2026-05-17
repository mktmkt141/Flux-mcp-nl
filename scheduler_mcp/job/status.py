from typing import Annotated, Any, Dict, Optional, Union

JobInfoResult = Annotated[
    Dict[str, Any],
    "Structured job status and metadata for a submitted Flux job.",
]


def flux_get_job_info(
    job_id: Annotated[Union[int, str], "Flux job identifier."],
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> JobInfoResult:
    """
    Retrieve status information about a specific Flux job.
    """
    try:
        import flux
        import flux.job

        handle = flux.Flux(uri) if uri else flux.Flux()
        flux_job_id = flux.job.JobID(job_id)
        info = dict(flux.job.get_job(handle, flux_job_id))
        return {"success": True, "error": None, "info": info}
    except EnvironmentError:
        return {"success": False, "error": f"Job {job_id} not found.", "info": None}
    except Exception as exc:
        return {"success": False, "error": str(exc), "info": None}
