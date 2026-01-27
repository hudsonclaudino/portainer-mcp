FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 8000

# Usamos server:mcp.sse_app que é a aplicação Starlette exposta pelo FastMCP
CMD ["uvicorn", "server:mcp.sse_app", "--host", "0.0.0.0", "--port", "8000"]