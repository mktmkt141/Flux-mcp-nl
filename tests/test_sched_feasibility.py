from scheduler_mcp.sched.feasibility import (
    check_job_request_sched_feasibility,
    flux_sched_resource_feasibility_check,
)


def test_flux_sched_resource_feasibility_check_success(monkeypatch):
    class FakeRPCResult:
        def get(self):
            return None

    class FakeHandle:
        def rpc(self, name, payload):
            assert name == "feasibility.check"
            assert payload["jobspec"]["version"] == 1
            return FakeRPCResult()

    class FakeFluxModule:
        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)

    result = flux_sched_resource_feasibility_check({"version": 1})

    assert result["success"] is True
    assert result["error"] is None
    assert result["satisfiable"] is True
    assert result["scheduler_message"] is None
    assert result["feasibility"]["satisfiable"] is True


def test_flux_sched_resource_feasibility_check_unsatisfiable(monkeypatch):
    class FakeHandle:
        def rpc(self, name, payload):
            raise OSError(19, "Unsatisfiable request")

    class FakeFluxModule:
        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)

    result = flux_sched_resource_feasibility_check({"version": 1})

    assert result["success"] is True
    assert result["error"] is None
    assert result["satisfiable"] is False
    assert "Unsatisfiable request" in result["scheduler_message"]
    assert result["feasibility"]["satisfiable"] is False


def test_flux_sched_resource_feasibility_check_failure(monkeypatch):
    class FakeHandle:
        def rpc(self, name, payload):
            raise RuntimeError("scheduler rpc failed")

    class FakeFluxModule:
        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)

    result = flux_sched_resource_feasibility_check({"version": 1})

    assert result["success"] is False
    assert result["error"] == "scheduler rpc failed"
    assert result["satisfiable"] is None
    assert result["feasibility"] is None


def test_check_job_request_sched_feasibility(monkeypatch):
    monkeypatch.setattr(
        "scheduler_mcp.sched.feasibility.convert_job_request_to_flux_jobspec",
        lambda job_request: {
            "success": True,
            "errors": [],
            "job_request": job_request,
            "jobspec": {"version": 1},
        },
    )
    monkeypatch.setattr(
        "scheduler_mcp.sched.feasibility.flux_sched_resource_feasibility_check",
        lambda jobspec_dict, uri=None: {
            "success": True,
            "error": None,
            "jobspec": jobspec_dict,
            "satisfiable": True,
            "scheduler_message": None,
            "feasibility": {"satisfiable": True, "note": "ok"},
        },
    )

    result = check_job_request_sched_feasibility(
        {
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
        }
    )

    assert result["success"] is True
    assert result["jobspec"]["version"] == 1
    assert result["satisfiable"] is True
    assert result["feasibility"]["satisfiable"] is True
    assert result["conversion_errors"] == []
