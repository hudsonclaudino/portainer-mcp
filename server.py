import os
import requests
import uvicorn
from mcp.server import Server
from mcp.server.sse import SseServerTransport
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.requests import Request
from starlette.responses import Response

# --- Configurações ---
PORTAINER_URL = os.getenv("PORTAINER_URL", "http://portainer:9000")
API_TOKEN = os.getenv("PORTAINER_API_KEY")

if not API_TOKEN:
    raise ValueError("A variavel de ambiente PORTAINER_API_KEY e obrigatoria.")

HEADERS = {"X-API-Key": API_TOKEN}

# --- Inicializa o Servidor MCP (Modo Server, não FastMCP) ---
mcp_server = Server("portainer-manager")

# --- Ferramentas ---
@mcp_server.tool()
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

@mcp_server.tool()
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

# --- Encanamento SSE (Server-Sent Events) ---
async def handle_sse(request: Request):
    async with mcp_server.create_initialization_context() as init_context:
        transport = SseServerTransport("/messages")
        async with transport.connect_sse(request.scope, request.receive, request._send) as streams:
            await mcp_server.run(streams[0], streams[1], init_context)

async def handle_messages(request: Request):
    # Endpoint para receber mensagens POST do cliente
    return Response("Not implemented (SSE only)", status_code=405) # Simplificacao, o transporte SSE lida com isso internamente via sessao

# Como configurar Starlette para MCP e complexo, vamos usar a rota direta do sse-transport se disponivel
# Ou usar o metodo manual simples:
async def sse_endpoint(request):
    transport = SseServerTransport("/messages")
    # A logica de conexao SSE manual requer cuidado com loops.
    # Vamos usar o 'sse_starlette' se possivel ou usar a implementacao padrao.
    pass

# --- SIMPLIFICAÇÃO ---
# Para não complicar com Starlette manual, vamos usar o wrapper do MCP se ele permitir,
# mas como falhou, vamos forcar o uvicorn no app Starlette.

from mcp.server.sse import SseServerTransport
from starlette.middleware import Middleware
from starlette.middleware.cors import CORSMiddleware

# Cria app Starlette
app = Starlette(debug=True)

# Endpoint SSE oficial
@app.route("/sse")
async def handle_sse_connect(request: Request):
    transport = SseServerTransport("/messages")
    async with mcp_server.create_initialization_context() as init_ctx:
        async with transport.connect_sse(request.scope, request.receive, request._send) as (read, write):
            await mcp_server.run(read, write, init_ctx)

@app.route("/messages", methods=["POST"])
async def handle_messages(request: Request):
    # O cliente MCP manda mensagens POST para cá
    await SseServerTransport("/messages").handle_post_message(request.scope, request.receive, request._send)

if __name__ == "__main__":
    # AQUI ESTÁ O SEGREDO: host="0.0.0.0"
    print("🚀 Iniciando Servidor MCP no IP 0.0.0.0...")
    uvicorn.run(app, host="0.0.0.0", port=8000)