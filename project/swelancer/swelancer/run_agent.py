from __future__ import annotations

import argparse
import json
import subprocess
from importlib import import_module
from pathlib import Path
from typing import Any

from swelancer.agent.agent_base import AgentBase
from swelancer.agent.docker_utils import (
    start_task_environment,
    teardown_task_environment,
)


def import_from_path(path: str) -> type[AgentBase]:
    module_name, cls_name = path.split(":")
    module = import_module(module_name)
    return getattr(module, cls_name)


def load_problem_statement(task_id: str) -> str:
    issue_path = (
        Path(__file__).resolve().parent.parent / "issues" / task_id / "issue_data.json"
    )
    with issue_path.open() as f:
        data = json.load(f)
    title = data.get("title", "")
    desc = data.get("html_description", "")
    return f"{title}\n\n{desc}"


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Run a single SWE-Lancer task with an agent"
    )
    parser.add_argument("task_id", help="Task identifier, e.g. 28565_1001")
    parser.add_argument(
        "agent", help="Import path to Agent class, e.g. mypkg.agent:MyAgent"
    )
    parser.add_argument(
        "--use-monolith", action="store_true", help="Use monolith docker image"
    )
    parser.add_argument("--image-prefix", default="swelancer/swelancer_x86")
    parser.add_argument("--image-tag", default="latest")
    args = parser.parse_args()

    env_info = start_task_environment(
        args.task_id,
        use_monolith=args.use_monolith,
        image_prefix=args.image_prefix,
        image_tag=args.image_tag,
    )

    problem_statement = load_problem_statement(args.task_id)

    agent_cls = import_from_path(args.agent)
    agent = agent_cls()

    output_schema = "choice" if env_info["task_type"] == "swe_manager" else "patch"
    solution = agent.predict(problem_statement, env_info, output_schema)

    if output_schema == "patch":
        apply_cmd = [
            "docker",
            "exec",
            env_info["container_id"],
            "bash",
            "-c",
            "git apply - && cd /app/expensify && pytest -q",
        ]
        res = subprocess.run(
            apply_cmd, input=str(solution).encode(), capture_output=True
        )
        success = res.returncode == 0
        print(res.stdout.decode())
    else:
        dest = json.dumps({"proposal_id": solution})
        subprocess.run(
            [
                "docker",
                "exec",
                env_info["container_id"],
                "bash",
                "-c",
                f"echo '{dest}' > /app/expensify/manager_decisions.json",
            ],
            check=True,
        )
        with open(
            Path(__file__).resolve().parent.parent / "all_swelancer_tasks.csv"
        ) as f:
            lines = [
                l for l in f.read().splitlines() if l.startswith(args.task_id + ",")
            ]
        gold_choice = None
        if lines:
            gold_choice = json.loads(lines[0].split(",")[-1])["game"][
                "correct_proposal"
            ]["id"]
        success = str(solution) == str(gold_choice)

    print("SUCCESS" if success else "FAILURE")
    teardown_task_environment(env_info)


if __name__ == "__main__":
    main()
