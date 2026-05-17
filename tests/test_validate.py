from scheduler_mcp.validate import (
    validate_flux_batch_script,
    validate_job_request_to_flux_batch_script,
    validate_natural_language_job_request,
    validate_natural_language_job_request_to_flux_batch_script,
)


def test_validate_flux_batch_script_success():
    script = "\n".join(
        [
            "#!/bin/bash",
            "# flux: -N 1",
            "# flux: -n 1",
            "# flux: -c 1",
            "# flux: -t 1800s",
            "",
            "hostname",
        ]
    )

    result = validate_flux_batch_script(script)

    assert result["success"] is True
    assert result["valid"] is True
    assert result["errors"] == []


def test_validate_flux_batch_script_failure():
    script = "\n".join(
        [
            "#!/bin/bash",
            "# flux -N 1",
            "",
            "hostname",
            "# flux: -t 1800s",
        ]
    )

    result = validate_flux_batch_script(script)

    assert result["success"] is True
    assert result["valid"] is False
    assert result["errors"]


def test_validate_job_request_to_flux_batch_script():
    result = validate_job_request_to_flux_batch_script(
        {
            "command": "python train.py",
            "job_name": "train-job",
            "num_nodes": 1,
            "num_tasks": 1,
            "cpus_per_task": 1,
            "gpus_per_task": 0,
            "wall_time": 1800,
            "working_directory": None,
            "environment": {},
            "output_file": None,
            "error_file": None,
        }
    )

    assert result["success"] is True
    assert result["valid"] is True
    assert result["job_request"]["command"] == "python train.py"


def test_validate_natural_language_job_request_to_flux_batch_script():
    result = validate_natural_language_job_request_to_flux_batch_script(
        "1ノードで30分使って hostname を実行したい"
    )

    assert result["success"] is True
    assert result["valid"] is True
    assert result["job_request"]["command"] == "hostname"


def test_validate_natural_language_job_request_consistent(monkeypatch):
    def fake_gemini_parse(text: str, model=None):
        return {
            "success": True,
            "errors": [],
            "job_request": {
                "command": "hostname",
                "job_name": None,
                "num_nodes": 1,
                "num_tasks": 1,
                "cpus_per_task": 1,
                "gpus_per_task": 0,
                "wall_time": 1800,
                "working_directory": None,
                "environment": {},
                "output_file": None,
                "error_file": None,
            },
        }

    monkeypatch.setattr(
        "scheduler_mcp.validate.validate.parse_natural_language_job_request_with_gemini",
        fake_gemini_parse,
    )

    result = validate_natural_language_job_request(
        "1ノードで30分使って hostname を実行したい"
    )

    assert result["success"] is True
    assert result["valid"] is True
    assert result["consistent"] is True
    assert "command" in result["matched_fields"]
    assert result["mismatched_fields"] == []


def test_validate_natural_language_job_request_mismatch(monkeypatch):
    def fake_gemini_parse(text: str, model=None):
        return {
            "success": True,
            "errors": [],
            "job_request": {
                "command": "python hostname.py",
                "job_name": None,
                "num_nodes": 1,
                "num_tasks": 1,
                "cpus_per_task": 2,
                "gpus_per_task": 0,
                "wall_time": 1800,
                "working_directory": None,
                "environment": {},
                "output_file": None,
                "error_file": None,
            },
        }

    monkeypatch.setattr(
        "scheduler_mcp.validate.validate.parse_natural_language_job_request_with_gemini",
        fake_gemini_parse,
    )

    result = validate_natural_language_job_request(
        "1ノードで30分使って hostname を実行したい"
    )

    assert result["success"] is True
    assert result["valid"] is False
    assert result["consistent"] is False
    assert "command" in result["mismatched_fields"]
    assert "cpus_per_task" in result["mismatched_fields"]
