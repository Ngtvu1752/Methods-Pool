from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from models.dataset_metadata import DatasetMetadata


@dataclass(frozen=True)
class ImageDataset:
    """Normalized object for image datasets."""

    metadata: DatasetMetadata
    path: Path
    image: Any | None = None
    width: int | None = None
    height: int | None = None
    mode: str | None = None
    source_format: str | None = None
    extra: dict[str, Any] = field(default_factory=dict)

    @property
    def dataset_id(self) -> str:
        return self.metadata.id
