from scheduler_mcp.tools.analysis import analyze_natural_language_job_request


def test_analyze_success(monkeypatch):
    def fake_feasibility(job_request, uri=None):
        return {
            "schedulable_now": True,
            "reasons": [],
            "requested": {
                "nodes": job_request["num_nodes"],
                "tasks": job_request["num_tasks"],
                "cores": job_request["num_tasks"] * job_request["cpus_per_task"],
                "gpus_per_task": job_request["gpus_per_task"],
                "wall_time": job_request["wall_time"],
                "command": job_request["command"],
            },
            "available": {
                "cores": 4,
                "gpus": 0,
                "nodes": 1,
                "hosts": ["test-host"],
                "ranks": [0],
                "properties": {},
            },
        }

    monkeypatch.setattr(
        "scheduler_mcp.tools.analysis.check_job_request_feasibility",
        fake_feasibility,
    )

    result = analyze_natural_language_job_request(
        "1ノードで30分使って hostname を実行したい"
    )

    assert result["success"] is True
    assert result["errors"] == []
    assert result["job_request"]["command"] == "hostname"
    assert result["feasibility"]["schedulable_now"] is True


def test_analyze_parse_failure():
    result = analyze_natural_language_job_request("2ノードで1時間使いたい")

    assert result["success"] is False
    assert result["job_request"] is None
    assert result["feasibility"] is None
    assert result["errors"]
