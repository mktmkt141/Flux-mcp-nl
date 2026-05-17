from scheduler_mcp.tools.convert import (
    convert_job_request_to_flux_batch_script,
    convert_natural_language_job_request_to_flux_batch_script,
)


def test_convert_job_request_to_flux_batch_script():
    result = convert_job_request_to_flux_batch_script(
        {
            "command": "python train.py",
            "job_name": "train-job",
            "num_nodes": 2,
            "num_tasks": 4,
            "cpus_per_task": 2,
            "gpus_per_task": 1,
            "wall_time": 3600,
        }
    )

    assert result["success"] is True
    script = result["script"]
    assert "#!/bin/bash" in script
    assert "# flux: --job-name=train-job" in script
    assert "# flux: -N 2" in script
    assert "# flux: -n 4" in script
    assert "# flux: -c 2" in script
    assert "# flux: -g 1" in script
    assert "# flux: -t 3600s" in script
    assert script.rstrip().endswith("python train.py")


def test_convert_natural_language_job_request_to_flux_batch_script():
    result = convert_natural_language_job_request_to_flux_batch_script(
        "1ノードで30分使って hostname を実行したい"
    )

    assert result["success"] is True
    assert result["job_request"]["command"] == "hostname"
    assert "# flux: -N 1" in result["script"]
    assert "# flux: -t 1800s" in result["script"]


def test_convert_natural_language_job_request_to_flux_batch_script_failure():
    result = convert_natural_language_job_request_to_flux_batch_script(
        "2ノードで1時間使いたい"
    )

    assert result["success"] is False
    assert result["job_request"] is None
    assert result["script"] is None
    assert result["errors"]


def test_convert_job_request_to_flux_batch_script_with_runtime_options():
    result = convert_job_request_to_flux_batch_script(
        {
            "command": "python train.py",
            "job_name": "train-job",
            "num_nodes": 1,
            "num_tasks": 1,
            "cpus_per_task": 1,
            "gpus_per_task": 0,
            "wall_time": 1800,
            "working_directory": "/work/project",
            "environment": {"OMP_NUM_THREADS": "1", "DATA_DIR": "/data"},
            "output_file": "stdout.log",
            "error_file": "stderr.log",
        }
    )

    script = result["script"]
    assert "export OMP_NUM_THREADS='1'" in script
    assert "export DATA_DIR='/data'" in script
    assert "cd /work/project" in script
    assert "python train.py > stdout.log 2> stderr.log" in script
