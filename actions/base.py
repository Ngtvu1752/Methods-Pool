from abc import ABC, abstractmethod
from typing import Any


class BaseAction(ABC):
    """Base interface for every action."""

    name: str = ""
    supported_dataset_types: tuple[type, ...] = ()

    def can_execute(self, dataset: Any) -> bool:
        return isinstance(dataset, self.supported_dataset_types)

    @abstractmethod
    def execute(self, dataset: Any, **kwargs: Any) -> dict[str, Any]:
        raise NotImplementedError