from __future__ import annotations

import subprocess
from typing import Any, Dict


def start_task_environment(
    task_id: str,
    use_monolith: bool = False,
    image_prefix: str = "swelancer/swelancer_x86",
    image_tag: str = "latest",
) -> Dict[str, Any]:
    """Start the Docker container for a given SWE-Lancer task.

    Parameters
    ----------
    task_id : str
        Identifier of the task (e.g. ``"28565_1001"``).
    use_monolith : bool, optional
        Whether to use the monolithic Docker image shared across tasks.
    image_prefix : str, optional
        Base name of the Docker image.
    image_tag : str, optional
        Tag of the Docker image to use.

    Returns
    -------
    dict
        Information about the running container, including ``container_id`` and
        ``task_type``.
    """
    image = (
        f"{image_prefix}_monolith:{image_tag}"
        if use_monolith
        else f"{image_prefix}_{task_id}:{image_tag}"
    )

    container_id = (
        subprocess.check_output(
            [
                "docker",
                "run",
                "-d",
                "--rm",
                "--entrypoint",
                "/app/runtime_scripts/run.sh",
                image,
            ]
        )
        .decode()
        .strip()
    )

    task_type = "swe_manager" if "manager" in task_id else "ic_swe"

    return {
        "container_id": container_id,
        "task_type": task_type,
        "image": image,
    }


def teardown_task_environment(env_info: Dict[str, Any]) -> None:
    """Stop and remove the Docker container associated with a task."""
    container_id = env_info.get("container_id")
    if not container_id:
        return
    subprocess.run(["docker", "stop", container_id], check=False)
