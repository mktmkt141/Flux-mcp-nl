from scheduler_mcp.sched.release import flux_sched_resource_cancel, flux_sched_resource_partial_cancel


def test_flux_sched_resource_cancel_success(monkeypatch):
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
            assert name == "sched-fluxion-resource.cancel"
            assert payload["jobid"].value == 3
            return FakeRPCResult({"status": "CANCELED"})

    class FakeFluxJobModule:
        JobID = FakeJobID

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)

    result = flux_sched_resource_cancel(3)

    assert result["success"] is True
    assert result["jobid"] == "3"
    assert result["result"]["status"] == "CANCELED"


def test_flux_sched_resource_cancel_failure(monkeypatch):
    class FakeJobID:
        def __init__(self, value):
            self.value = value

    class FakeHandle:
        def rpc(self, name, payload=None):
            raise RuntimeError("release failed")

    class FakeFluxJobModule:
        JobID = FakeJobID

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)

    result = flux_sched_resource_cancel(4)

    assert result["success"] is False
    assert result["jobid"] == "4"
    assert result["result"] is None


def test_flux_sched_resource_partial_cancel_success(monkeypatch):
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
            assert name == "sched-fluxion-resource.partial-cancel"
            assert payload["jobid"].value == 5
            assert payload["R"] == "{\"demo\":true}"
            return FakeRPCResult({"status": "PARTIAL_CANCELED"})

    class FakeFluxJobModule:
        JobID = FakeJobID

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)

    result = flux_sched_resource_partial_cancel(5, '{"demo":true}')

    assert result["success"] is True
    assert result["jobid"] == "5"
    assert result["result"]["status"] == "PARTIAL_CANCELED"
