import json
import os
import urllib.error
import urllib.parse
import urllib.request
from typing import Annotated, Any, Dict

from scheduler_mcp.models import JobRequest

DEFAULT_MODEL = "gemini-2.5-flash-lite"
DEFAULT_ENDPOINT = "https://generativelanguage.googleapis.com/v1beta/models"

JOB_REQUEST_SCHEMA = {
    "type": "object",
    "properties": {
        "command": {
            "type": "string",
            "description": "The shell command to run, such as python train.py or hostname.",
        },
        "job_name": {
            "type": ["string", "null"],
            "description": "Optional job name. Use null if not specified.",
        },
        "num_nodes": {
            "type": "integer",
            "description": "Requested number of nodes. Default to 1 when unspecified.",
        },
        "num_tasks": {
            "type": "integer",
            "description": "Requested number of tasks. Default to 1 when unspecified.",
        },
        "cpus_per_task": {
            "type": "integer",
            "description": "Requested CPU cores per task. Default to 1 when unspecified.",
        },
        "gpus_per_task": {
            "type": "integer",
            "description": "Requested GPUs per task. Default to 0 when unspecified.",
        },
        "wall_time": {
            "type": ["integer", "null"],
            "description": "Requested wall time in seconds. Use null if not specified.",
        },
        "working_directory": {
            "type": ["string", "null"],
            "description": "Directory where the command should be executed. Use null if not specified.",
        },
        "environment": {
            "type": "object",
            "description": "Environment variables to export before execution. Use an empty object if not specified.",
            "additionalProperties": {"type": "string"},
        },
        "output_file": {
            "type": ["string", "null"],
            "description": "Optional file path for stdout redirection. Use null if not specified.",
        },
        "error_file": {
            "type": ["string", "null"],
            "description": "Optional file path for stderr redirection. Use null if not specified.",
        },
    },
    "required": [
        "command",
        "job_name",
        "num_nodes",
        "num_tasks",
        "cpus_per_task",
        "gpus_per_task",
        "wall_time",
        "working_directory",
        "environment",
        "output_file",
        "error_file",
    ],
    "additionalProperties": False,
}


def _gemini_request_body(text: str) -> Dict[str, Any]:
    return {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "Extract a structured HPC job request from the following Japanese text. "
                            "Return only JSON that matches the schema. "
                            "If a field is not specified, use these defaults: "
                            "job_name=null, num_nodes=1, num_tasks=1, cpus_per_task=1, "
                            "gpus_per_task=0, wall_time=null, working_directory=null, "
                            "environment={}, output_file=null, error_file=null. "
                            "The command field must contain the executable shell command.\n\n"
                            f"Input: {text}"
                        )
                    }
                ]
            }
        ],
        "generationConfig": {
            "responseMimeType": "application/json",
            "responseJsonSchema": JOB_REQUEST_SCHEMA,
        },
    }


def _call_gemini_api(text: str, api_key: str, model: str) -> Dict[str, Any]:
    endpoint = f"{DEFAULT_ENDPOINT}/{urllib.parse.quote(model, safe='')}:" "generateContent"
    url = f"{endpoint}?key={urllib.parse.quote(api_key)}"
    body = json.dumps(_gemini_request_body(text)).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.loads(response.read().decode("utf-8"))

    parts = payload["candidates"][0]["content"]["parts"]
    output_text = "".join(part.get("text", "") for part in parts)
    return json.loads(output_text)


def parse_natural_language_job_request_with_gemini(
    text: Annotated[str, "Natural-language job request in Japanese."],
    model: Annotated[
        str | None,
        "Optional Gemini model name. Defaults to GEMINI_MODEL or gemini-2.5-flash-lite.",
    ] = None,
):
    """
    Parse a Japanese natural-language job request into JobRequest using the Gemini API.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return {
            "success": False,
            "errors": ["GEMINI_API_KEY is not set."],
            "job_request": None,
        }

    selected_model = model or os.getenv("GEMINI_MODEL") or DEFAULT_MODEL

    try:
        payload = _call_gemini_api(text=text, api_key=api_key, model=selected_model)
        job_request = JobRequest(**payload)
    except urllib.error.HTTPError as exc:
        return {
            "success": False,
            "errors": [f"Gemini API HTTP error: {exc.code} {exc.reason}"],
            "job_request": None,
        }
    except Exception as exc:
        return {
            "success": False,
            "errors": [f"Gemini API request failed: {exc}"],
            "job_request": None,
        }

    if not job_request.command.strip():
        return {
            "success": False,
            "errors": ["Gemini returned an empty command."],
            "job_request": None,
        }

    return {"success": True, "errors": [], "job_request": job_request.to_dict()}


def analyze_natural_language_job_request_with_gemini(
    text: Annotated[str, "Natural-language job request in Japanese."],
    uri: Annotated[
        str | None,
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
    model: Annotated[
        str | None,
        "Optional Gemini model name. Defaults to GEMINI_MODEL or gemini-2.5-flash-lite.",
    ] = None,
):
    """
    Parse a natural-language job request with Gemini and evaluate whether it appears schedulable now.
    """
    from scheduler_mcp.analysis.feasibility import check_job_request_feasibility

    parse_result = parse_natural_language_job_request_with_gemini(text=text, model=model)
    if not parse_result["success"]:
        return {
            "success": False,
            "errors": parse_result["errors"],
            "job_request": None,
            "feasibility": None,
        }

    job_request = parse_result["job_request"]
    feasibility = check_job_request_feasibility(job_request=job_request, uri=uri)

    return {
        "success": True,
        "errors": [],
        "job_request": job_request,
        "feasibility": feasibility,
    }


def submit_natural_language_job_request_to_flux_with_gemini(
    text: Annotated[str, "Natural-language job request in Japanese."],
    model: Annotated[
        str | None,
        "Optional Gemini model name. Defaults to GEMINI_MODEL or gemini-2.5-flash-lite.",
    ] = None,
):
    """
    Parse a natural-language request with Gemini and submit it to Flux.
    """
    from scheduler_mcp.job.submit import submit_job_request_to_flux

    parse_result = parse_natural_language_job_request_with_gemini(text=text, model=model)
    if not parse_result["success"]:
        return {
            "success": False,
            "errors": parse_result["errors"],
            "job_request": None,
            "script": None,
            "job_id": None,
        }

    return submit_job_request_to_flux(parse_result["job_request"])
