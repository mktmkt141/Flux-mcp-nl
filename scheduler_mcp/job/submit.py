import os
import subprocess
import tempfile
from typing import Annotated, Any, Dict

from scheduler_mcp.transform.convert import (
    convert_job_request_to_flux_batch_script,
    convert_natural_language_job_request_to_flux_batch_script,
)

JobSubmissionResult = Annotated[
    Dict[str, Any],
    "Result of submitting a Flux batch script, including success, errors, and job_id.",
]


def _submit_flux_batch_script(script: str) -> subprocess.CompletedProcess[str]:
    with tempfile.NamedTemporaryFile("w", suffix=".sh", delete=False) as handle:
        handle.write(script)
        temp_path = handle.name

    os.chmod(temp_path, 0o755)
    try:
        return subprocess.run(
            ["flux", "batch", temp_path],
            capture_output=True,
            text=True,
            check=False,
        )
    finally:
        os.unlink(temp_path)


def submit_job_request_to_flux(
    job_request: Annotated[
        Dict[str, Any],
        "Structured job request to convert and submit to Flux.",
    ],
) -> JobSubmissionResult:
    """
    Convert a JobRequest into a Flux batch script and submit it with `flux batch`.
    """
    conversion = convert_job_request_to_flux_batch_script(job_request)
    if not conversion["success"]:
        return {
            "success": False,
            "errors": conversion["errors"],
            "job_request": None,
            "script": None,
            "job_id": None,
        }

    script = conversion["script"]
    result = _submit_flux_batch_script(script)
    stdout = result.stdout.strip()
    stderr = result.stderr.strip()

    if result.returncode != 0:
        return {
            "success": False,
            "errors": [stderr or stdout or "flux batch failed"],
            "job_request": job_request,
            "script": script,
            "job_id": None,
        }

    job_id = stdout.splitlines()[0] if stdout else None
    return {
        "success": True,
        "errors": [],
        "job_request": job_request,
        "script": script,
        "job_id": job_id,
    }


def submit_natural_language_job_request_to_flux(
    text: Annotated[str, "Natural-language job request in Japanese."],
) -> JobSubmissionResult:
    """
    Parse a natural-language request, convert it into a Flux batch script, and submit it.
    """
    conversion = convert_natural_language_job_request_to_flux_batch_script(text)
    if not conversion["success"]:
        return {
            "success": False,
            "errors": conversion["errors"],
            "job_request": None,
            "script": None,
            "job_id": None,
        }

    return submit_job_request_to_flux(conversion["job_request"])
