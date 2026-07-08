from mcp.server.fastmcp import FastMCP

from catalog import DataLakeCatalog
from config import DATA_LAKE_ROOT
from hub import DataLakeHub
import actions  # Import side effects register available actions.
import readers  # Import side effects register available readers.


mcp = FastMCP("data-lake")

catalog = DataLakeCatalog(root_path=DATA_LAKE_ROOT)
hub = DataLakeHub(catalog=catalog)


@mcp.tool()
async def list_datasets(
    modality: str | None = None,
    processing_domain: str | None = None,
) -> list[dict]:
    """List approved datasets in the local data lake.

    Args:
        modality: Optional high-level group, such as structured,
            unstructured, or multimodal.
        processing_domain: Optional processing type, such as tabular,
            plain_text, markdown, web_page, or sql_script.
    """
    return await hub.list_datasets(
        modality=modality,
        processing_domain=processing_domain,
    )


@mcp.tool()
async def get_dataset_metadata(dataset_id: str) -> dict:
    """Get metadata for one approved dataset."""
    return await hub.get_dataset_metadata(dataset_id)


@mcp.tool()
async def preview_dataset(
    dataset_id: str,
    limit: int = 20,
) -> dict:
    """Preview rows or lines from an approved dataset."""
    return await hub.execute_action(
        action_name="preview",
        dataset_id=dataset_id,
        limit=limit,
    )


@mcp.tool()
async def get_dataset_schema(dataset_id: str) -> dict:
    """Get schema information for a dataset when available."""
    return await hub.execute_action(
        action_name="schema",
        dataset_id=dataset_id,
    )


@mcp.tool()
async def refresh_catalog() -> dict:
    """Refresh the in-memory catalog by scanning the data lake folder."""
    return hub.refresh_catalog()


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
