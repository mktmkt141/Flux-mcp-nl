from scheduler_mcp.sched.info import (
    flux_sched_qmanager_stats,
    flux_sched_resource_find,
    flux_sched_resource_get_property,
    flux_sched_resource_info,
    flux_sched_resource_ns_info,
    flux_sched_resource_params,
    flux_sched_resource_remove_property,
    flux_sched_resource_set_property,
    flux_sched_resource_set_status,
    flux_sched_resource_stats,
    flux_sched_resource_stats_clear,
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


def test_flux_sched_resource_property_and_status_calls(monkeypatch):
    class FakeRPCResult:
        def __init__(self, payload):
            self.payload = payload

        def get(self):
            return self.payload

    calls = []

    class FakeHandle:
        def rpc(self, name, payload=None):
            calls.append((name, payload))
            return FakeRPCResult({"ok": True})

    class FakeFluxModule:
        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)

    set_result = flux_sched_resource_set_property("node0", "group=test")
    get_result = flux_sched_resource_get_property("node0", "group")
    remove_result = flux_sched_resource_remove_property("node0", "group")
    status_result = flux_sched_resource_set_status("node0", "down")

    assert set_result["success"] is True
    assert get_result["success"] is True
    assert remove_result["success"] is True
    assert status_result["success"] is True
    assert calls[0][0] == "sched-fluxion-resource.set_property"
    assert calls[0][1] == {"sp_resource_path": "node0", "sp_keyval": "group=test"}
    assert calls[1][0] == "sched-fluxion-resource.get_property"
    assert calls[1][1] == {"gp_resource_path": "node0", "gp_key": "group"}
    assert calls[2][0] == "sched-fluxion-resource.remove_property"
    assert calls[2][1] == {"resource_path": "node0", "key": "group"}
    assert calls[3][0] == "sched-fluxion-resource.set_status"
    assert calls[3][1] == {"resource_path": "node0", "status": "down"}


def test_flux_sched_resource_stats_params_ns_info(monkeypatch):
    class FakeRPCResult:
        def __init__(self, payload):
            self.payload = payload

        def get(self):
            return self.payload

    calls = []

    class FakeHandle:
        def rpc(self, name, payload=None):
            calls.append((name, payload))
            mapping = {
                "sched-fluxion-resource.stats-get": {"matches": 1},
                "sched-fluxion-resource.stats-clear": {},
                "sched-fluxion-resource.params": {"policy": "high"},
                "sched-fluxion-resource.ns-info": {"id": 99},
            }
            return FakeRPCResult(mapping[name])

    class FakeFluxModule:
        @staticmethod
        def Flux(uri=None):
            return FakeHandle()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)

    stats_result = flux_sched_resource_stats()
    clear_result = flux_sched_resource_stats_clear()
    params_result = flux_sched_resource_params()
    ns_result = flux_sched_resource_ns_info(0, "core", 3)

    assert stats_result["success"] is True
    assert stats_result["stats"]["matches"] == 1
    assert clear_result["success"] is True
    assert params_result["params"]["policy"] == "high"
    assert ns_result["result"]["id"] == 99
    assert calls[3][0] == "sched-fluxion-resource.ns-info"
    assert calls[3][1] == {"rank": 0, "type-name": "core", "id": 3}
