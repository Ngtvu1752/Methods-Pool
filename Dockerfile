FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DATA_LAKE_ROOT=/app/Data-Lake
ENV MCP_TRANSPORT=streamable-http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8000

WORKDIR /app/Methods-Hub

COPY requirements.txt /app/Methods-Hub/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/Methods-Hub

EXPOSE 8000

CMD ["python", "main.py"]
