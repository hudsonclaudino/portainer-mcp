FROM python:3.11-slim

WORKDIR /app

# Instala dependências
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copia o código
COPY server.py .

# Expose a porta padrão do FastMCP/Uvicorn (geralmente 8000)
EXPOSE 8000

# Comando para rodar o servidor SSE
CMD ["python", "server.py"]