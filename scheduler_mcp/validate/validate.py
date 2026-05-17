from typing import Annotated, Any, Dict, List

from scheduler_mcp.transform.convert import (
    convert_job_request_to_flux_batch_script,
    convert_natural_language_job_request_to_flux_batch_script,
)
from scheduler_mcp.transform.gemini_nl import parse_natural_language_job_request_with_gemini
from scheduler_mcp.transform.nl import parse_natural_language_job_request

FluxBatchValidationResult = Annotated[
    Dict[str, Any],
    "Validation result for a Flux batch script including valid flag and any errors.",
]
NaturalLanguageValidationResult = Annotated[
    Dict[str, Any],
    "Validation result comparing rule-based and Gemini natural-language parsing.",
]

_ALLOWED_SHORT_DIRECTIVES = {"-N", "-n", "-c", "-g", "-t"}
_ALLOWED_LONG_DIRECTIVES = {"--job-name"}
_JOB_REQUEST_COMPARE_FIELDS = [
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
]


def _validate_directive(line: str, errors: List[str], line_number: int) -> None:
    directive = line[len("# flux:") :].strip()
    if not directive:
        errors.append(f"Line {line_number}: empty Flux directive.")
        return

    token = directive.split()[0]
    if "=" in token:
        token = token.split("=", 1)[0]

    if token in _ALLOWED_SHORT_DIRECTIVES:
        if token == "-t":
            parts = directive.split(maxsplit=1)
            value = parts[1].strip() if len(parts) > 1 else ""
            if not value.endswith("s") or not value[:-1].isdigit():
                errors.append(
                    f"Line {line_number}: time directive must be an integer number of seconds, e.g. '# flux: -t 1800s'."
                )
        else:
            parts = directive.split(maxsplit=1)
            value = parts[1].strip() if len(parts) > 1 else ""
            if not value.isdigit():
                errors.append(
                    f"Line {line_number}: directive '{token}' must be followed by a positive integer value."
                )
        return

    if any(token.startswith(name) for name in _ALLOWED_LONG_DIRECTIVES):
        if token == "--job-name":
            parts = directive.split(maxsplit=1)
            if len(parts) < 2 or not parts[1].strip():
                errors.append(f"Line {line_number}: --job-name requires a value.")
        return

    errors.append(f"Line {line_number}: unknown Flux directive '{token}'.")


def validate_flux_batch_script(
    script: Annotated[str, "Flux batch script content to validate."],
) -> FluxBatchValidationResult:
    """
    Perform lightweight validation of a generated Flux batch script before submit.
    """
    errors: List[str] = []
    lines = script.splitlines()

    if not script.strip():
        errors.append("Script is empty.")
        return {"success": True, "valid": False, "errors": errors, "script": script}

    if not lines or lines[0].strip() != "#!/bin/bash":
        errors.append("First line must be '#!/bin/bash'.")

    saw_command = False
    command_lines = 0
    for index, raw_line in enumerate(lines[1:], start=2):
        line = raw_line.strip()
        if not line:
            continue

        if line.lower().startswith("# flux "):
            errors.append(
                f"Line {index}: Flux directives must use '# flux:' with a colon."
            )
            continue

        if line.lower().startswith("# flux:"):
            if saw_command:
                errors.append(
                    f"Line {index}: Flux directives must appear before command lines."
                )
                continue
            _validate_directive(line, errors, index)
            continue

        if not line.startswith("#"):
            saw_command = True
            command_lines += 1

    if command_lines == 0:
        errors.append("Script must contain at least one command line.")

    return {
        "success": True,
        "valid": not errors,
        "errors": errors,
        "script": script,
    }


def validate_job_request_to_flux_batch_script(
    job_request: Annotated[
        Dict[str, Any],
        "Structured job request to convert and validate as a Flux batch script.",
    ],
) -> FluxBatchValidationResult:
    """
    Convert a JobRequest to a Flux batch script and validate the generated script.
    """
    conversion = convert_job_request_to_flux_batch_script(job_request)
    if not conversion["success"]:
        return {
            "success": False,
            "valid": False,
            "errors": conversion["errors"],
            "script": None,
            "job_request": None,
        }

    validation = validate_flux_batch_script(conversion["script"])
    validation["job_request"] = conversion["job_request"]
    return validation


def validate_natural_language_job_request_to_flux_batch_script(
    text: Annotated[str, "Natural-language job request in Japanese."],
) -> FluxBatchValidationResult:
    """
    Convert a natural-language request to a Flux batch script and validate it.
    """
    conversion = convert_natural_language_job_request_to_flux_batch_script(text)
    if not conversion["success"]:
        return {
            "success": False,
            "valid": False,
            "errors": conversion["errors"],
            "script": None,
            "job_request": None,
        }

    validation = validate_flux_batch_script(conversion["script"])
    validation["job_request"] = conversion["job_request"]
    return validation


def validate_natural_language_job_request(
    text: Annotated[str, "Natural-language job request in Japanese."],
    model: Annotated[
        str | None,
        "Optional Gemini model name. Defaults to GEMINI_MODEL or gemini-2.5-flash-lite.",
    ] = None,
) -> NaturalLanguageValidationResult:
    """
    Compare rule-based and Gemini parsing results for the same natural-language request.
    """
    rule_result = parse_natural_language_job_request(text)
    gemini_result = parse_natural_language_job_request_with_gemini(text=text, model=model)

    if not rule_result["success"] or not gemini_result["success"]:
        errors: List[str] = []
        if not rule_result["success"]:
            errors.extend([f"rule_based: {msg}" for msg in rule_result["errors"]])
        if not gemini_result["success"]:
            errors.extend([f"gemini: {msg}" for msg in gemini_result["errors"]])
        return {
            "success": False,
            "valid": False,
            "errors": errors,
            "consistent": False,
            "matched_fields": [],
            "mismatched_fields": [],
            "rule_based_job_request": rule_result.get("job_request"),
            "gemini_job_request": gemini_result.get("job_request"),
        }

    rule_job_request = rule_result["job_request"]
    gemini_job_request = gemini_result["job_request"]
    matched_fields: List[str] = []
    mismatched_fields: List[str] = []

    for field_name in _JOB_REQUEST_COMPARE_FIELDS:
        if rule_job_request.get(field_name) == gemini_job_request.get(field_name):
            matched_fields.append(field_name)
        else:
            mismatched_fields.append(field_name)

    return {
        "success": True,
        "valid": not mismatched_fields,
        "errors": [],
        "consistent": not mismatched_fields,
        "matched_fields": matched_fields,
        "mismatched_fields": mismatched_fields,
        "rule_based_job_request": rule_job_request,
        "gemini_job_request": gemini_job_request,
    }
