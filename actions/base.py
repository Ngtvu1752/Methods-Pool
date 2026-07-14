from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ActionParam:
    """Runtime-declared parameter for generated MCP tools."""

    name: str
    type: type
    default: Any = None
    description: str = ""


class BaseAction(ABC):
    """Base interface for every action."""

    name: str = ""
    description: str = ""
    params: tuple[ActionParam, ...] = ()
    supported_dataset_types: tuple[type, ...] = ()

    def can_execute(self, dataset: Any) -> bool:
        return isinstance(dataset, self.supported_dataset_types)

    @abstractmethod
    def execute(self, dataset: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError
