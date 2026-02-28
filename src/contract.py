from typing import Protocol, runtime_checkable, List, Dict, Any, Union
from dataclasses import dataclass
from typing_extensions import TypeAlias
from uuid import uuid4

from typing import Protocol, runtime_checkable, List

@dataclass
class Task:
    id: str
    payload: Any

    @classmethod
    def create(cls, payload: Any) -> "Task":
        return cls(id=str(uuid4()), payload=payload)

@runtime_checkable
class TaskSource(Protocol):
    def get_tasks(self) -> List[Task]:
        """
        Get all tasks
        :return: List of Task
        """
        ...