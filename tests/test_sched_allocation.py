from scheduler_mcp.sched.allocation import (
    check_job_request_sched_allocate,
    flux_sched_resource_allocate_with_satisfiability,
)


def test_flux_sched_resource_allocate_with_satisfiability_success(monkeypatch):
    class FakeRPCResult:
        def __init__(self, payload):
            self.payload = payload

        def get(self):
            return self.payload

    class FakeJobID:
        def __init__(self, value):
            self.value = value

    class FakeHandle:
        def rpc(self, name, payload=None):
            if name == "sched-fluxion-resource.next_jobid":
                return FakeRPCResult({"jobid": 7})
            if name == "sched-fluxion-resource.match":
                assert payload["cmd"] == "allocate_with_satisfiability"
                assert payload["jobspec"]
                return FakeRPCResult({"jobid": 7, "status": "ALLOCATED", "R": "demo"})
            raise AssertionError(f"unexpected rpc: {name}")

    class FakeFluxJobModule:
        JobID = FakeJobID

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)

    result = flux_sched_resource_allocate_with_satisfiability({"version": 1})

    assert result["success"] is True
    assert result["allocation"]["status"] == "ALLOCATED"
    assert result["allocation"]["jobid"] == 7


def test_flux_sched_resource_allocate_with_satisfiability_failure(monkeypatch):
    class FakeHandle:
        def rpc(self, name, payload=None):
            raise RuntimeError("allocation rpc failed")

    class FakeFluxJobModule:
        class JobID:
            def __init__(self, value):
                self.value = value

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)

    result = flux_sched_resource_allocate_with_satisfiability({"version": 1})

    assert result["success"] is False
    assert result["error"] == "allocation rpc failed"
    assert result["allocation"] is None


def test_check_job_request_sched_allocate(monkeypatch):
    monkeypatch.setattr(
        "scheduler_mcp.sched.allocation.convert_job_request_to_flux_jobspec",
        lambda job_request: {
            "success": True,
            "errors": [],
            "job_request": job_request,
            "jobspec": {"version": 1},
        },
    )
    monkeypatch.setattr(
        "scheduler_mcp.sched.allocation.flux_sched_resource_allocate_with_satisfiability",
        lambda jobspec_dict, uri=None: {
            "success": True,
            "error": None,
            "jobspec": jobspec_dict,
            "allocation": {"jobid": 3, "status": "ALLOCATED", "R": "demo"},
        },
    )

    result = check_job_request_sched_allocate(
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
    assert result["allocation"]["status"] == "ALLOCATED"
    assert result["allocation"]["jobid"] == 3
    assert result["conversion_errors"] == []
