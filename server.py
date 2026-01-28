import os
import requests
import uvicorn
from mcp.server.fastmcp import FastMCP

# --- Configurações ---
PORTAINER_URL = os.getenv("PORTAINER_URL", "http://portainer:9000")
API_TOKEN = os.getenv("PORTAINER_API_KEY")

if not API_TOKEN:
    raise ValueError("A variavel de ambiente PORTAINER_API_KEY e obrigatoria.")

HEADERS = {"X-API-Key": API_TOKEN}

# --- Inicializa o Servidor MCP (Modo FastMCP) ---
# Usando FastMCP para simplificar a definição de ferramentas e transporte
mcp = FastMCP("portainer-manager", host="0.0.0.0")

# --- Ferramentas ---
@mcp.tool()
async def list_stacks() -> str:
    """Lista todas as Stacks do Portainer. Retorna: ID, Nome, Status."""
    try:
        url = f"{PORTAINER_URL}/api/stacks"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        stacks = resp.json()
        
        if not stacks: return "Nenhuma stack encontrada."

        output = []
        for s in stacks:
            status = "Ativo" if s.get('Status') == 1 else f"Status-{s.get('Status')}"
            output.append(f"ID: {s['Id']} | Name: {s['Name']} | Status: {status}")
        return "\n".join(output)
    except Exception as e:
        return f"Erro ao conectar ao Portainer: {str(e)}"

@mcp.tool()
async def get_stack_file(stack_id: int) -> str:
    """Lê o arquivo docker-compose.yml de uma stack pelo ID."""
    try:
        url = f"{PORTAINER_URL}/api/stacks/{stack_id}/file"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return data.get("StackFileContent", "Conteudo vazio.")
    except Exception as e:
        return f"Erro ao ler stack {stack_id}: {str(e)}"

if __name__ == "__main__":
    print("🚀 Iniciando Servidor MCP no IP 0.0.0.0...")
    # FastMCP fornece uma aplicação Starlette configurada para SSE via .sse_app
    uvicorn.run(mcp.sse_app, host="0.0.0.0", port=8000)