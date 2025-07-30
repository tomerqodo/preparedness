import os
import subprocess
import sys
from pathlib import Path

import pytest

from swelancer.agent.docker_utils import (
    start_task_environment,
    teardown_task_environment,
)
sys.path.append(str(Path(__file__).resolve().parent))
from gold_patch_agent import GoldPatchAgent
from swelancer.run_agent import load_problem_statement
from swelancer.utils.general import is_docker_running


@pytest.mark.integration
@pytest.mark.skipif(
    not is_docker_running(),
    reason="Docker daemon must be running to execute integration test.",
)
def test_run_agent_end_to_end():
    task_id = "28565_1001"
    try:
        env_info = start_task_environment(task_id, use_monolith=False)
    except Exception as e:
        pytest.skip(f"Environment setup failed: {e}")

    problem = load_problem_statement(task_id)
    agent = GoldPatchAgent(task_id)
    patch = agent.predict(problem, env_info, "patch")

    apply_cmd = [
        "docker",
        "exec",
        env_info["container_id"],
        "bash",
        "-c",
        "git apply - && cd /app/expensify && pytest -q",
    ]
    res = subprocess.run(apply_cmd, input=patch.encode(), capture_output=True)
    teardown_task_environment(env_info)
    assert res.returncode == 0
