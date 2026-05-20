from scheduler_mcp.job.cancel import flux_cancel_job


def test_flux_cancel_job_success(monkeypatch):
    class FakeJobID:
        def __init__(self, value):
            self.value = value

    class FakeFluxJobModule:
        JobID = FakeJobID

        @staticmethod
        def cancel(handle, job_id):
            return None

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return object()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)

    result = flux_cancel_job("f123")

    assert result["success"] is True
    assert result["error"] is None
    assert result["job_id"] == "f123"
    assert "cancellation requested" in result["message"]


def test_flux_cancel_job_failure(monkeypatch):
    class FakeJobID:
        def __init__(self, value):
            self.value = value

    class FakeFluxJobModule:
        JobID = FakeJobID

        @staticmethod
        def cancel(handle, job_id):
            raise RuntimeError("cancel failed")

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return object()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)

    result = flux_cancel_job("f123")

    assert result["success"] is False
    assert result["job_id"] == "f123"
    assert result["error"] == "cancel failed"
    assert "Cancellation had an error" == result["message"]
