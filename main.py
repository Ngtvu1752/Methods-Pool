from mcp.server.fastmcp import FastMCP

from catalog import DataLakeCatalog
from config import DATA_LAKE_ROOT
from hub import DataLakeHub
import actions  # Import side effects register available actions.
import readers  # Import side effects register available readers.
from actions.registry import ActionRegistry
from tools import build_all_tools


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
async def refresh_catalog() -> dict:
    """Refresh the in-memory catalog by scanning the data lake folder."""
    return hub.refresh_catalog()


@mcp.tool()
async def list_methods() -> list[dict]:
    """List methods available in this Methods Hub."""
    return ActionRegistry.list_methods()


@mcp.tool()
async def search_methods(query: str) -> list[dict]:
    """Search available methods by name, description, params, or dataset type."""
    return ActionRegistry.search_methods(query)


@mcp.tool()
async def inspect_method(method_name: str) -> dict:
    """Inspect one method, including params and supported dataset types."""
    return ActionRegistry.inspect_method(method_name)


for tool_func in build_all_tools(hub):
    mcp.tool()(tool_func)


def main():
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
