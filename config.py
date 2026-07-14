import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_LAKE_ROOT = Path(
    os.getenv("DATA_LAKE_ROOT", str(PROJECT_ROOT / "Data-Lake"))
).resolve()
MCP_TRANSPORT = os.getenv("MCP_TRANSPORT", "streamable-http")
MCP_HOST = os.getenv("MCP_HOST", "0.0.0.0")
MCP_PORT = int(os.getenv("MCP_PORT", "8000"))
