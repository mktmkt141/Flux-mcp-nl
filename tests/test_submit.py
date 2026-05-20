import subprocess

from scheduler_mcp.job.submit import (
    submit_job_request_to_flux,
    submit_natural_language_job_request_to_flux,
)


def test_submit_job_request_to_flux_success(monkeypatch):
    def fake_submit(script):
        return subprocess.CompletedProcess(
            args=["flux", "batch", "tmp.sh"],
            returncode=0,
            stdout="f123456\n",
            stderr="",
        )

    monkeypatch.setattr(
        "scheduler_mcp.job.submit._submit_flux_batch_script", fake_submit
    )

    result = submit_job_request_to_flux(
        {
            "command": "hostname",
            "num_nodes": 1,
            "num_tasks": 1,
            "cpus_per_task": 1,
            "gpus_per_task": 0,
            "wall_time": 1800,
        }
    )

    assert result["success"] is True
    assert result["job_id"] == "f123456"
    assert "# flux: -N 1" in result["script"]


def test_submit_job_request_to_flux_failure(monkeypatch):
    def fake_submit(script):
        return subprocess.CompletedProcess(
            args=["flux", "batch", "tmp.sh"],
            returncode=1,
            stdout="",
            stderr="submission failed",
        )

    monkeypatch.setattr(
        "scheduler_mcp.job.submit._submit_flux_batch_script", fake_submit
    )

    result = submit_job_request_to_flux(
        {
            "command": "hostname",
            "num_nodes": 1,
            "num_tasks": 1,
            "cpus_per_task": 1,
            "gpus_per_task": 0,
            "wall_time": 1800,
        }
    )

    assert result["success"] is False
    assert result["job_id"] is None
    assert result["errors"]


def test_submit_natural_language_job_request_to_flux_parse_failure():
    result = submit_natural_language_job_request_to_flux("2ノードで1時間使いたい")

    assert result["success"] is False
    assert result["job_request"] is None
    assert result["script"] is None
    assert result["job_id"] is None
