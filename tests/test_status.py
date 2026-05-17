from scheduler_mcp.tools.status import flux_get_job_info


def test_flux_get_job_info_success(monkeypatch):
    class FakeJobID:
        def __init__(self, value):
            self.value = value

    class FakeFluxJobModule:
        JobID = FakeJobID

        @staticmethod
        def get_job(handle, job_id):
            return {
                "id": job_id.value,
                "state": "RUN",
                "status": "RUN",
                "result": "",
            }

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return object()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)

    result = flux_get_job_info("f123")

    assert result["success"] is True
    assert result["error"] is None
    assert result["info"]["id"] == "f123"
    assert result["info"]["status"] == "RUN"


def test_flux_get_job_info_failure(monkeypatch):
    class FakeJobID:
        def __init__(self, value):
            self.value = value

    class FakeFluxJobModule:
        JobID = FakeJobID

        @staticmethod
        def get_job(handle, job_id):
            raise EnvironmentError("not found")

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return object()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)

    result = flux_get_job_info("missing")

    assert result["success"] is False
    assert result["info"] is None
    assert "missing" in result["error"]
