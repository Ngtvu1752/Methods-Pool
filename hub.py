from typing import Any

from actions.registry import ActionRegistry
from catalog import DataLakeCatalog
from models import DatasetMetadata
from readers.registry import ReaderRegistry

class DataLakeHub:
    def __init__(
        self,
        catalog: DataLakeCatalog,
        reader_registry: type[ReaderRegistry] = ReaderRegistry,
        action_registry: type[ActionRegistry] = ActionRegistry,
    ):
        self.catalog = catalog
        self.reader_registry = reader_registry
        self.action_registry = action_registry
    
    async def list_datasets(
        self,
        modality: str | None = None,
        processing_domain: str | None = None,
    ) -> list[dict]:
        datasets = self.catalog.list_datasets(
            modality=modality,
            processing_domain=processing_domain,
        )
        return [self._serialize_dataset(dataset) for dataset in datasets]

    async def get_dataset_metadata(self, dataset_id: str) -> dict:
        dataset = self.catalog.get_dataset(dataset_id)
        return self._serialize_dataset(dataset)

    async def execute_action(
        self,
        action_name: str,
        dataset_id: str,
        **kwargs: Any,
    ) -> dict:
        loaded_dataset = self._load_dataset(dataset_id)
        action = self.action_registry.get(action_name, loaded_dataset)
        return action.execute(loaded_dataset, **kwargs)

    def refresh_catalog(self) -> dict:
        self.catalog.refresh()
        return {"status": "ok", "message": "Catalog refreshed."}

    def _load_dataset(self, dataset_id: str) -> Any:
        dataset = self.catalog.get_dataset(dataset_id)
        reader = self.reader_registry.get(dataset.file_format)
        return reader.read(dataset)

    def _serialize_dataset(self, dataset: DatasetMetadata) -> dict:
        return {
            "id": dataset.id,
            "name": dataset.name,
            "file_format": dataset.file_format,
            "modality": dataset.modality,
            "processing_domain": dataset.processing_domain,
            "size_bytes": dataset.size_bytes,
        }
