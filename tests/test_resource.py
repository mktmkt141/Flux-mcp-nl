from types import SimpleNamespace

from scheduler_mcp.tools import resource


class FakeBucket:
    def __init__(self, ncores, ngpus, nnodes, nodelist, ranks, properties):
        self.ncores = ncores
        self.ngpus = ngpus
        self.nnodes = nnodes
        self.nodelist = nodelist
        self.ranks = ranks
        self._properties = properties

    def get_properties(self):
        return self._properties


def test_get_flux_resource_list(monkeypatch):
    fake_listing = SimpleNamespace(
        free=FakeBucket(4, 1, 1, ["node1"], [0], '{"queue":"debug"}'),
        up=FakeBucket(8, 1, 2, ["node1", "node2"], [0, 1], '{"queue":"batch"}'),
    )

    monkeypatch.setattr(resource, "_get_handle", lambda uri=None: object())
    monkeypatch.setattr(resource, "_load_flux_resource_listing", lambda handle: fake_listing)

    result = resource.get_flux_resource_list()

    assert result["free"]["cores"] == 4
    assert result["free"]["gpus"] == 1
    assert result["up"]["nodes"] == 2
    assert result["up"]["properties"]["queue"] == "batch"
