from abc import ABC, abstractmethod
from typing import Any

from models import DatasetMetadata


class BaseReader(ABC):
    """
    Base interface for every readers
    """

    supported_formats: set[str] = set()

    @abstractmethod
    def read(self, dataset: DatasetMetadata) -> Any:
        """
        Read the dataset and return its content.
        """
        raise NotImplementedError("Subclasses must implement the read method.")

