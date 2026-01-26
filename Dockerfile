FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .

EXPOSE 8000

# TRUQUE: Acessamos a app interna do FastMCP (_sse_app)
# Isso força o host 0.0.0.0 sem precisar mudar código Python
CMD ["uvicorn", "server:mcp._sse_app", "--host", "0.0.0.0", "--port", "8000"]