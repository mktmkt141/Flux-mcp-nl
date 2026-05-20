from scheduler_mcp.analysis.feasibility import check_job_request_feasibility


def test_feasible_job_request(monkeypatch):
    def fake_resource_report(uri=None):
        return {
            "free": {
                "cores": 4,
                "gpus": 0,
                "nodes": 1,
                "hosts": ["test-host"],
                "ranks": [0],
                "properties": {},
            },
            "up": {
                "cores": 4,
                "gpus": 0,
                "nodes": 1,
                "hosts": ["test-host"],
                "ranks": [0],
                "properties": {},
            },
        }

    monkeypatch.setattr(
        "scheduler_mcp.analysis.feasibility.get_flux_resource_list", fake_resource_report
    )

    result = check_job_request_feasibility(
        {
            "command": "hostname",
            "num_nodes": 1,
            "num_tasks": 1,
            "cpus_per_task": 2,
            "gpus_per_task": 0,
            "wall_time": 60,
        }
    )

    assert result["schedulable_now"] is True
    assert result["reasons"] == []
    assert result["requested"]["cores"] == 2


def test_infeasible_job_request(monkeypatch):
    def fake_resource_report(uri=None):
        return {
            "free": {
                "cores": 4,
                "gpus": 0,
                "nodes": 1,
                "hosts": ["test-host"],
                "ranks": [0],
                "properties": {},
            },
            "up": {
                "cores": 4,
                "gpus": 0,
                "nodes": 1,
                "hosts": ["test-host"],
                "ranks": [0],
                "properties": {},
            },
        }

    monkeypatch.setattr(
        "scheduler_mcp.analysis.feasibility.get_flux_resource_list", fake_resource_report
    )

    result = check_job_request_feasibility(
        {
            "command": "python train.py",
            "num_nodes": 2,
            "num_tasks": 3,
            "cpus_per_task": 2,
            "gpus_per_task": 1,
            "wall_time": 3600,
        }
    )

    assert result["schedulable_now"] is False
    assert len(result["reasons"]) == 3
