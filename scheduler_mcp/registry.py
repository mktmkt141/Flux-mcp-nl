from scheduler_mcp.analysis import analyze_natural_language_job_request, check_job_request_feasibility
from scheduler_mcp.job import (
    flux_cancel_job,
    flux_get_job_logs,
    flux_get_job_info,
    submit_job_request_to_flux,
    submit_natural_language_job_request_to_flux,
)
from scheduler_mcp.resource import get_flux_resource_list
from scheduler_mcp.sched import (
    check_job_request_sched_allocate,
    check_job_request_sched_feasibility,
    flux_sched_resource_allocate_with_satisfiability,
    flux_sched_resource_feasibility_check,
)
from scheduler_mcp.transform import (
    analyze_natural_language_job_request_with_gemini,
    convert_job_request_to_flux_batch_script,
    convert_job_request_to_flux_jobspec,
    convert_natural_language_job_request_to_flux_batch_script,
    parse_natural_language_job_request,
    parse_natural_language_job_request_with_gemini,
    submit_natural_language_job_request_to_flux_with_gemini,
)
from scheduler_mcp.validate import (
    validate_flux_batch_script,
    validate_job_request_to_flux_batch_script,
    validate_natural_language_job_request,
    validate_natural_language_job_request_to_flux_batch_script,
)

TOOLS = [
    analyze_natural_language_job_request,
    analyze_natural_language_job_request_with_gemini,
    convert_natural_language_job_request_to_flux_batch_script,
    convert_job_request_to_flux_batch_script,
    convert_job_request_to_flux_jobspec,
    parse_natural_language_job_request_with_gemini,
    parse_natural_language_job_request,
    check_job_request_feasibility,
    flux_sched_resource_allocate_with_satisfiability,
    flux_sched_resource_feasibility_check,
    check_job_request_sched_allocate,
    check_job_request_sched_feasibility,
    get_flux_resource_list,
    flux_cancel_job,
    flux_get_job_info,
    flux_get_job_logs,
    submit_natural_language_job_request_to_flux_with_gemini,
    submit_natural_language_job_request_to_flux,
    submit_job_request_to_flux,
    validate_flux_batch_script,
    validate_job_request_to_flux_batch_script,
    validate_natural_language_job_request,
    validate_natural_language_job_request_to_flux_batch_script,
]
