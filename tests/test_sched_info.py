from scheduler_mcp.sched.info import (
    flux_sched_qmanager_stats,
    flux_sched_resource_find,
    flux_sched_resource_info,
    flux_sched_resource_status,
)


def test_flux_sched_qmanager_stats_success(monkeypatch):
    class FakeRPCResult:
        def __init__(self, payload):
            self.payload = payload

        def get(self):
            return self.payload

    class FakeHandle:
        def rpc(self, name, payload=None):
            assert name == "sched-fluxion-qmanager.stats-get"
            return FakeRPCResult({"default": {"depth": 1, "running": 2}})

    class FakeFluxModule:
        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)

    result = flux_sched_qmanager_stats()

    assert result["success"] is True
    assert result["stats"]["default"]["depth"] == 1


def test_flux_sched_resource_info_success(monkeypatch):
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
            assert name == "sched-fluxion-resource.info"
            assert payload["jobid"].value == 5
            return FakeRPCResult({"status": "ALLOCATED", "overhead": 0.01})

    class FakeFluxJobModule:
        JobID = FakeJobID

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)

    result = flux_sched_resource_info(5)

    assert result["success"] is True
    assert result["jobid"] == "5"
    assert result["resource_info"]["status"] == "ALLOCATED"


def test_flux_sched_resource_info_failure(monkeypatch):
    class FakeJobID:
        def __init__(self, value):
            self.value = value

    class FakeHandle:
        def rpc(self, name, payload=None):
            raise RuntimeError("resource info failed")

    class FakeFluxJobModule:
        JobID = FakeJobID

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)

    result = flux_sched_resource_info(8)

    assert result["success"] is False
    assert result["jobid"] == "8"
    assert result["resource_info"] is None


def test_flux_sched_resource_status_success(monkeypatch):
    class FakeRPCResult:
        def __init__(self, payload):
            self.payload = payload

        def get(self):
            return self.payload

    class FakeHandle:
        def rpc(self, name, payload=None):
            assert name == "sched-fluxion-resource.status"
            return FakeRPCResult({"all": {"up": ["node0"], "allocated": ["node1"]}})

    class FakeFluxModule:
        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)

    result = flux_sched_resource_status()

    assert result["success"] is True
    assert result["resource_status"]["all"]["up"] == ["node0"]


def test_flux_sched_resource_find_success(monkeypatch):
    class FakeRPCResult:
        def __init__(self, payload):
            self.payload = payload

        def get(self):
            return self.payload

    class FakeHandle:
        def rpc(self, name, payload=None):
            assert name == "sched-fluxion-resource.find"
            assert payload["criteria"] == "status=up"
            assert payload["format"] == "json"
            return FakeRPCResult({"matches": ["node0", "node1"]})

    class FakeFluxModule:
        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)

    result = flux_sched_resource_find("status=up", find_format="json")

    assert result["success"] is True
    assert result["criteria"] == "status=up"
    assert result["resource_find"]["matches"] == ["node0", "node1"]
