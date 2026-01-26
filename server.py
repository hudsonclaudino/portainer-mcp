import os
import requests
from mcp.server.fastmcp import FastMCP

# Configurações via Variáveis de Ambiente
PORTAINER_URL = os.getenv("PORTAINER_URL", "http://portainer:9000")
API_TOKEN = os.getenv("PORTAINER_API_KEY")

if not API_TOKEN:
    raise ValueError("A variável de ambiente PORTAINER_API_KEY é obrigatória.")

HEADERS = {"X-API-Key": API_TOKEN}

# Inicializa o servidor MCP
mcp = FastMCP("Portainer Manager")

@mcp.tool()
def list_stacks() -> str:
    """
    Lista todas as Stacks do Portainer.
    Retorna: ID, Nome, Status e EndpointID.
    """
    try:
        url = f"{PORTAINER_URL}/api/stacks"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        stacks = resp.json()
        
        if not stacks:
            return "Nenhuma stack encontrada."

        output = []
        for s in stacks:
            # Status 1=Active, 2=Inactive (pode variar conforme versão)
            status = "Ativo" if s.get('Status') == 1 else f"Status-Code-{s.get('Status')}"
            output.append(f"ID: {s['Id']} | Name: {s['Name']} | Status: {status}")
        
        return "\n".join(output)
    except Exception as e:
        return f"Erro ao conectar ao Portainer: {str(e)}"

@mcp.tool()
def get_stack_file(stack_id: int) -> str:
    """
    Lê o arquivo docker-compose.yml (StackFileContent) de uma stack específica.
    Args:
        stack_id: O ID numérico da stack (obtido via list_stacks).
    """
    try:
        url = f"{PORTAINER_URL}/api/stacks/{stack_id}/file"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        
        content = data.get("StackFileContent")
        if not content:
            return "Conteúdo do arquivo não encontrado ou vazio."
            
        return content
    except Exception as e:
        return f"Erro ao ler arquivo da stack {stack_id}: {str(e)}"

if __name__ == "__main__":
    import uvicorn
    
    # O FastMCP força '127.0.0.1' internamente. Vamos interceptar a chamada 
    # do uvicorn para forçar '0.0.0.0' e permitir acesso externo ao Docker.
    original_run = uvicorn.run

    def patched_run(app, **kwargs):
        # Sobrescreve host e port para garantir acesso externo
        kwargs["host"] = "0.0.0.0"
        kwargs["port"] = 8000
        print(f"🔧 Patch aplicado: Iniciando Uvicorn em {kwargs['host']}:{kwargs['port']}")
        return original_run(app, **kwargs)

    # Aplica o patch
    uvicorn.run = patched_run
    
    # Inicia o servidor normalmente (sem argumentos extras que causam erro)
    mcp.run(transport="sse")