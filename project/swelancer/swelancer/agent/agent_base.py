from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Tuple


class AgentBase(ABC):
    """Base class for agents solving SWE-Lancer tasks.

    Parameters
    ----------
    **config : Any
        Arbitrary configuration options used by the agent. These are stored on
        ``self.config`` for later access.
    """

    def __init__(self, **config: Any) -> None:
        self.config = config

    @abstractmethod
    def predict(
        self,
        problem_statement: str,
        environment_info: dict[str, Any],
        output_schema: Any,
    ) -> str | Tuple[str, ...]:
        """Generate a solution for a SWE-Lancer task.

        Parameters
        ----------
        problem_statement : str
            The textual description of the task the agent must solve.
        environment_info : dict[str, Any]
            Information about the running task environment. This may contain a
            Docker container ID, repository paths, or other details needed by
            the agent to interact with the task.
        output_schema : Any
            Indicator of the expected output format. ``"patch"`` indicates the
            agent must return a unified diff patch string for an Independent
            Coding task, while ``"choice"`` indicates a proposal selection for a
            SWE Manager task.

        Returns
        -------
        str | Tuple[str, ...]
            The agent's solution. For coding tasks this should be a unified diff
            patch as a string. For manager tasks it should be the selected
            proposal identifier.
        """
        raise NotImplementedError
