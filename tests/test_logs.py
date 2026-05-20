import os

from scheduler_mcp.job.logs import flux_get_job_logs


def test_flux_get_job_logs_success(monkeypatch):
    class FakeJobID:
        def __init__(self, value):
            self.value = value

    class FakeFluxJobModule:
        JobID = FakeJobID

        @staticmethod
        def get_job(handle, job_id):
            return {"cwd": "/tmp/test-logs", "jobid": job_id.value}

        @staticmethod
        def event_watch(handle, job_id, event_name):
            raise AssertionError("event_watch should not be used when output file exists")

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return object()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)
    monkeypatch.setattr("scheduler_mcp.job.logs.os.path.exists", lambda path: True)

    def fake_open(path, mode="r", encoding=None):
        class FakeFile:
            def __enter__(self):
                return self

            def __exit__(self, exc_type, exc, tb):
                return False

            def readlines(self):
                return ["ce88e08a04d2\n"]

        return FakeFile()

    monkeypatch.setattr("builtins.open", fake_open)

    result = flux_get_job_logs("f123")

    assert result["success"] is True
    assert result["error"] is None
    assert result["lines"] == ["ce88e08a04d2\n"]
    assert result["complete"] is True


def test_flux_get_job_logs_failure(monkeypatch):
    class FakeJobID:
        def __init__(self, value):
            self.value = value

    class FakeFluxJobModule:
        JobID = FakeJobID

        @staticmethod
        def get_job(handle, job_id):
            return {"cwd": "/tmp/test-logs", "jobid": job_id.value}

        @staticmethod
        def event_watch(handle, job_id, event_name):
            raise RuntimeError("boom")

    class FakeFluxModule:
        job = FakeFluxJobModule

        @staticmethod
        def Flux(uri=None):
            return object()

    monkeypatch.setitem(__import__("sys").modules, "flux", FakeFluxModule)
    monkeypatch.setitem(__import__("sys").modules, "flux.job", FakeFluxJobModule)
    monkeypatch.setattr("scheduler_mcp.job.logs.os.path.exists", lambda path: False)

    result = flux_get_job_logs("missing")

    assert result["success"] is False
    assert result["lines"] is None
    assert result["error"]
