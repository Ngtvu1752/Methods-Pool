from dataclasses import dataclass, field
from typing import Any

from models.dataset_metadata import DatasetMetadata


@dataclass(frozen=True)
class DocumentDataset:
    """Normalized object for text and document-like datasets."""

    metadata: DatasetMetadata
    text: str
    source_format: str | None = None
    title: str | None = None
    page_count: int | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def dataset_id(self) -> str:
        return self.metadata.id
