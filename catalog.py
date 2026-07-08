from pathlib import Path

from errors import UnsafePathError, DatasetNotFoundError
from models import DatasetMetadata

FORMAT_CLASSIFICATION = {
    ".csv": ("structured", "tabular"),
    ".xlsx": ("structured", "spreadsheet"),
    ".xls": ("structured", "spreadsheet"),
    ".txt": ("unstructured", "plain_text"),
    ".md": ("unstructured", "markdown"),
    ".html": ("unstructured", "web_page"),
    ".pdf": ("unstructured", "document"),
    ".docx": ("unstructured", "document"),
    ".ppt": ("unstructured", "presentation"),
    ".pptx": ("unstructured", "presentation"),
    ".sql": ("structured", "sql_script"),
    ".jpg": ("multimodal", "image"),
    ".jpeg": ("multimodal", "image"),
    ".png": ("multimodal", "image"),
    ".m4a": ("multimodal", "audio"),
    ".mp3": ("multimodal", "audio"),
    ".wav": ("multimodal", "audio"),
}

class DataLakeCatalog:
    def __init__(self, root_path: Path):
        self.root_path = root_path.resolve()
        self._datasets: dict[str, DatasetMetadata] = {}
        self.refresh()

    def refresh(self) -> None:
        """Refresh the catalog by scanning the data lake directory."""
        self._datasets = {}
        for path in self.root_path.rglob("*"):
            if not path.is_file():
                continue

            suffix = path.suffix.lower()
            if suffix not in FORMAT_CLASSIFICATION:
                continue

            self._ensure_safe_path(path)

            modality, processing_domain = FORMAT_CLASSIFICATION[suffix]
            dataset_id = path.relative_to(self.root_path).as_posix()

            self._datasets[dataset_id] = DatasetMetadata(
                id=dataset_id,
                name=path.name,
                path=path,
                file_format=suffix.removeprefix("."),
                modality=modality,
                processing_domain=processing_domain,
                size_bytes=path.stat().st_size,
            )
    
    def list_datasets(
        self,
        modality: str | None = None,
        processing_domain: str | None = None,
    ) -> list[DatasetMetadata]:
        """List all datasets in the catalog."""
        datasets = list(self._datasets.values())

        if modality is not None:
            datasets = [
                dataset for dataset in datasets
                if dataset.modality == modality
            ]

        if processing_domain is not None:
            datasets = [
                dataset for dataset in datasets
                if dataset.processing_domain == processing_domain
            ]

        return datasets
    
    def get_dataset(self, dataset_id:str) -> DatasetMetadata:
        """Get metadata for a specific dataset by its ID."""
        try: 
            return self._datasets[dataset_id]
        except KeyError:
            raise DatasetNotFoundError(dataset_id)
    
    def _ensure_safe_path(self, path: Path) -> None:
        resolved = path.resolve()

        if self.root_path not in resolved.parents and self.root_path != resolved:
            raise UnsafePathError(str(path))
            
