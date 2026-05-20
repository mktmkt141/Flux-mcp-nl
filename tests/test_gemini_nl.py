from scheduler_mcp.transform.gemini_nl import (
    analyze_natural_language_job_request_with_gemini,
    parse_natural_language_job_request_with_gemini,
    submit_natural_language_job_request_to_flux_with_gemini,
)


def test_gemini_parse_returns_error_without_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)

    result = parse_natural_language_job_request_with_gemini(
        "1ノードで30分使って hostname を実行したい"
    )

    assert result["success"] is False
    assert result["job_request"] is None
    assert "GEMINI_API_KEY" in result["errors"][0]


def test_gemini_parse_success(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "test-key")

    def fake_call(text: str, api_key: str, model: str):
        assert api_key == "test-key"
        assert model == "gemini-2.5-flash-lite"
        assert "hostname" in text
        return {
            "command": "hostname",
            "job_name": None,
            "num_nodes": 1,
            "num_tasks": 1,
            "cpus_per_task": 1,
            "gpus_per_task": 0,
            "wall_time": 1800,
        }

    monkeypatch.setattr("scheduler_mcp.transform.gemini_nl._call_gemini_api", fake_call)

    result = parse_natural_language_job_request_with_gemini(
        "1ノードで30分使って hostname を実行したい"
    )

    assert result["success"] is True
    assert result["errors"] == []
    assert result["job_request"]["command"] == "hostname"
    assert result["job_request"]["wall_time"] == 1800
    assert result["job_request"]["working_directory"] is None
    assert result["job_request"]["environment"] == {}
    assert result["job_request"]["output_file"] is None
    assert result["job_request"]["error_file"] is None


def test_gemini_analyze_success(monkeypatch):
    def fake_parse(text: str, model=None):
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
            },
        }

    def fake_feasibility(job_request, uri=None):
        return {
            "schedulable_now": True,
            "reasons": [],
            "requested": {"command": job_request["command"]},
            "available": {"nodes": 1, "cores": 4, "gpus": 0},
        }

    monkeypatch.setattr(
        "scheduler_mcp.transform.gemini_nl.parse_natural_language_job_request_with_gemini",
        fake_parse,
    )
    monkeypatch.setattr(
        "scheduler_mcp.transform.gemini_nl.check_job_request_feasibility",
        fake_feasibility,
    )

    result = analyze_natural_language_job_request_with_gemini(
        "1ノードで30分使って hostname を実行したい"
    )

    assert result["success"] is True
    assert result["feasibility"]["schedulable_now"] is True


def test_gemini_submit_success(monkeypatch):
    def fake_parse(text: str, model=None):
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
            },
        }

    def fake_submit(job_request):
        return {
            "success": True,
            "errors": [],
            "job_request": job_request,
            "script": "#!/bin/bash\nhostname",
            "job_id": "job-123",
        }

    monkeypatch.setattr(
        "scheduler_mcp.transform.gemini_nl.parse_natural_language_job_request_with_gemini",
        fake_parse,
    )
    monkeypatch.setattr(
        "scheduler_mcp.transform.gemini_nl.submit_job_request_to_flux",
        fake_submit,
    )

    result = submit_natural_language_job_request_to_flux_with_gemini(
        "1ノードで30分使って hostname を実行したい"
    )

    assert result["success"] is True
    assert result["job_id"] == "job-123"
