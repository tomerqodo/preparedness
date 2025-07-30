from __future__ import annotations

from pathlib import Path

from swelancer.agent.agent_base import AgentBase


def _reverse_patch(patch: str) -> str:
    lines = []
    for line in patch.splitlines():
        if line.startswith('+++') or line.startswith('---'):
            lines.append(line)
        elif line.startswith('+'):
            lines.append('-' + line[1:])
        elif line.startswith('-'):
            lines.append('+' + line[1:])
        else:
            lines.append(line)
    return '\n'.join(lines) + '\n'


class GoldPatchAgent(AgentBase):
    """Agent that returns the known correct patch for a task."""

    def __init__(self, task_id: str, **config: object) -> None:
        super().__init__(**config)
        self.task_id = task_id

    def predict(
        self, problem_statement: str, environment_info: dict, output_schema: object
    ) -> str:
        assert output_schema == "patch"
        patch_path = (
            Path(__file__).resolve().parent.parent
            / "issues"
            / self.task_id
            / "bug_reintroduce.patch"
        )
        with patch_path.open() as f:
            bug_patch = f.read()
        return _reverse_patch(bug_patch)
