from scheduler_mcp.transform.nl import parse_natural_language_job_request


def test_parse_training_request():
    result = parse_natural_language_job_request(
        "2ノード、各ノード4コアで1時間使って python train.py を実行したい"
    )

    assert result["success"] is True
    job_request = result["job_request"]
    assert job_request["num_nodes"] == 2
    assert job_request["cpus_per_task"] == 4
    assert job_request["wall_time"] == 3600
    assert job_request["command"] == "python train.py"


def test_parse_gpu_request():
    result = parse_natural_language_job_request(
        "GPUを1枚使って30分以内に evaluate.sh を流したい"
    )

    assert result["success"] is True
    job_request = result["job_request"]
    assert job_request["gpus_per_task"] == 1
    assert job_request["wall_time"] == 1800
    assert job_request["command"] == "evaluate.sh"


def test_parse_failure_without_command():
    result = parse_natural_language_job_request("2ノードで1時間使いたい")

    assert result["success"] is False
    assert result["job_request"] is None
    assert result["errors"]
