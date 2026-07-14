# Run Methods Hub With Docker

This MCP server runs with HTTP transport by default inside Docker.

## Requirements

- Docker
- Docker Compose
- A local data lake folder. In this repo, the default folder is:

```bash
/home/ngtvu/MCP-Server/Data-Lake
```

## Build And Run

From the repository root:

```bash
cd /home/ngtvu/MCP-Server/Methods-Hub
docker compose up --build
```

The MCP HTTP server will listen on:

```text
http://localhost:8000/mcp
```

## Run In Background

```bash
cd /home/ngtvu/MCP-Server/Methods-Hub
docker compose up --build -d
```

View logs:

```bash
docker compose logs -f methods-hub
```

Stop the server:

```bash
docker compose down
```

## Data Lake Mount

The compose file mounts the repo data lake as read-only:

```yaml
volumes:
  - ../Data-Lake:/app/Data-Lake:ro
```

Inside the container, the server reads data from:

```text
/app/Data-Lake
```

This is configured by:

```yaml
environment:
  DATA_LAKE_ROOT: /app/Data-Lake
```

To use another local data lake, change the left side of the volume:

```yaml
volumes:
  - /path/to/your/data-lake:/app/Data-Lake:ro
```

## HTTP Transport Config

The Docker setup uses:

```yaml
environment:
  MCP_TRANSPORT: streamable-http
  MCP_HOST: 0.0.0.0
  MCP_PORT: 8000
```

You can change the exposed host port if needed:

```yaml
ports:
  - "9000:8000"
```

Then the server will be available from the host at:

```text
http://localhost:9000/mcp
```

## Notes About Requirements

Current `requirements.txt` is intentionally small:

```text
mcp[cli]>=1.28.1
uvicorn>=0.30.0
```

That is enough for the current Methods Hub server because the implemented readers/actions use Python standard library modules only.

If you later add actions/readers that use pandas, DuckDB, Polars, Excel parsing, PDF parsing, OCR, or audio/video processing, add those packages to `requirements.txt`.

Examples:

```text
pandas
duckdb
polars
openpyxl
pypdf
python-docx
pillow
```
