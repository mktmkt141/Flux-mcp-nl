from scheduler_mcp.sched.helpers import (
    assess_job_request_submission_readiness,
    flux_sched_verify_resource_property_roundtrip,
    flux_sched_verify_resource_status_roundtrip,
    summarize_sched_verification_scenarios,
)


def test_flux_sched_verify_resource_property_roundtrip(monkeypatch):
    def fake_set(resource_path, key_val, uri=None):
        return {
            "success": True,
            "error": None,
            "resource_path": resource_path,
            "key_val": key_val,
            "result": {},
        }

    state = {"present": True}

    def fake_get(resource_path, key, uri=None):
        if state["present"]:
            return {
                "success": True,
                "error": None,
                "resource_path": resource_path,
                "key": key,
                "result": {"values": ["verify"]},
            }
        return {
            "success": False,
            "error": "missing",
            "resource_path": resource_path,
            "key": key,
            "result": None,
        }

    def fake_remove(resource_path, key, uri=None):
        state["present"] = False
        return {
            "success": True,
            "error": None,
            "resource_path": resource_path,
            "key": key,
            "result": {},
        }

    monkeypatch.setattr("scheduler_mcp.sched.helpers.flux_sched_resource_set_property", fake_set)
    monkeypatch.setattr("scheduler_mcp.sched.helpers.flux_sched_resource_get_property", fake_get)
    monkeypatch.setattr("scheduler_mcp.sched.helpers.flux_sched_resource_remove_property", fake_remove)

    result = flux_sched_verify_resource_property_roundtrip("/cluster0/node0", "group", "verify")

    assert result["success"] is True
    assert result["verified"] is True
    assert result["steps"]["get_property_after_set"]["result"]["values"] == ["verify"]
    assert result["steps"]["get_property_after_remove"]["success"] is False


def test_flux_sched_verify_resource_status_roundtrip(monkeypatch):
    snapshots = [
        {"success": True, "error": None, "resource_status": {"all": "before"}},
        {"success": True, "error": None, "resource_status": {"all": "during"}},
        {"success": True, "error": None, "resource_status": {"all": "after"}},
    ]

    def fake_status(uri=None):
        return snapshots.pop(0)

    calls = []

    def fake_set_status(resource_path, status, uri=None):
        calls.append((resource_path, status))
        return {
            "success": True,
            "error": None,
            "resource_path": resource_path,
            "status": status,
            "result": None,
        }

    monkeypatch.setattr("scheduler_mcp.sched.helpers.flux_sched_resource_status", fake_status)
    monkeypatch.setattr("scheduler_mcp.sched.helpers.flux_sched_resource_set_status", fake_set_status)

    result = flux_sched_verify_resource_status_roundtrip("/cluster0/node0/core0")

    assert result["success"] is True
    assert calls == [
        ("/cluster0/node0/core0", "down"),
        ("/cluster0/node0/core0", "up"),
    ]
    assert result["steps"]["before_status"]["resource_status"]["all"] == "before"
    assert result["steps"]["during_status"]["resource_status"]["all"] == "during"
    assert result["steps"]["after_status"]["resource_status"]["all"] == "after"


def test_assess_job_request_submission_readiness(monkeypatch):
    job_request = {
        "command": "hostname",
        "job_name": None,
        "num_nodes": 1,
        "num_tasks": 1,
        "cpus_per_task": 1,
        "gpus_per_task": 0,
        "wall_time": 60,
        "working_directory": None,
        "environment": {},
        "output_file": None,
        "error_file": None,
    }

    monkeypatch.setattr(
        "scheduler_mcp.sched.helpers.check_job_request_feasibility",
        lambda req, uri=None: {"schedulable_now": True, "reasons": [], "requested": {}, "available": {}},
    )
    monkeypatch.setattr(
        "scheduler_mcp.sched.helpers.check_job_request_sched_feasibility",
        lambda req, uri=None: {"success": True, "error": None, "satisfiable": True},
    )

    result = assess_job_request_submission_readiness(job_request)

    assert result["success"] is True
    assert result["recommendation"] == "submit_now"


def test_summarize_sched_verification_scenarios():
    result = summarize_sched_verification_scenarios()

    assert result["success"] is True
    names = [scenario["name"] for scenario in result["scenarios"]]
    assert "allocation" in names
    assert "property_roundtrip" in names
