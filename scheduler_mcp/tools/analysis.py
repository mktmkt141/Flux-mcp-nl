from typing import Annotated, Any, Dict, Optional

from scheduler_mcp.tools.feasibility import check_job_request_feasibility
from scheduler_mcp.tools.nl import parse_natural_language_job_request

AnalyzeJobRequestResult = Annotated[
    Dict[str, Any],
    "Combined result of parsing a natural-language job request and checking its current feasibility.",
]


def analyze_natural_language_job_request(
    text: Annotated[str, "Natural-language job request in Japanese."],
    uri: Annotated[
        Optional[str],
        "The Flux connection URI. Defaults to the local instance.",
    ] = None,
) -> AnalyzeJobRequestResult:
    """
    Parse a natural-language job request and immediately evaluate whether it appears schedulable now.
    """
    parse_result = parse_natural_language_job_request(text)
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
