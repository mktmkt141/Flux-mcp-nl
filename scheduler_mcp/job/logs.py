import os
import time
from typing import Annotated, Any, Dict, List, Optional, Union

LogLinesResult = Annotated[
    Dict[str, Any],
    "A dictionary containing success, error, lines, return_code, and complete for Flux job output logs.",
]


def flux_get_job_logs(
    job_id: Annotated[Union[int, str], "Flux job identifier."],
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
    delay: Annotated[
        Optional[int],
        "Maximum number of seconds to wait while collecting logs. If omitted, wait until complete.",
    ] = None,
) -> LogLinesResult:
    """
    Retrieve output logs associated with a specific Flux job.
    """
    lines: List[str] = []
    start = time.time()
    complete = False

    try:
        import flux
        import flux.job

        handle = flux.Flux(uri) if uri else flux.Flux()
        flux_job_id = flux.job.JobID(job_id)
        info = dict(flux.job.get_job(handle, flux_job_id))
        output_path = None
        if info.get("cwd") and info.get("jobid"):
            output_path = os.path.join(info["cwd"], f"flux-{info['jobid']}.out")

        if output_path and os.path.exists(output_path):
            with open(output_path, "r", encoding="utf-8") as infile:
                return {
                    "success": True,
                    "error": None,
                    "lines": infile.readlines(),
                    "return_code": 0,
                    "complete": True,
                }

        event_watch = flux.job.event_watch(handle, flux_job_id, "guest.output")
        if event_watch is None:
            return {
                "success": False,
                "error": "Job not ready or does not exist",
                "lines": None,
                "return_code": -1,
                "complete": False,
            }

        complete = True
        for line in event_watch:
            if not line:
                continue
            if "data" in line.context:
                lines.append(line.context["data"])

            if delay is not None and (time.time() - start) > delay:
                complete = False
                break

    except Exception as exc:
        return {
            "success": False,
            "error": str(exc),
            "lines": None,
            "return_code": -1,
            "complete": complete,
        }

    return {
        "success": True,
        "error": None,
        "lines": lines,
        "return_code": 0,
        "complete": complete,
    }
