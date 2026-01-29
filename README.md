# Portainer MCP Server

Este projeto implementa um servidor MCP (Model Context Protocol) que permite conectar agentes de IA (como Claude Desktop, Antigravity, etc.) ao seu gerenciador de containers Portainer.

Com ele, seu agente pode listar stacks e ler o conteúdo dos arquivos `docker-compose.yml` diretamente, facilitando a gestão e análise de infraestrutura via chat.

## 🚀 Tecnologias Utilizadas

- **Python 3.10+**
- **[MCP (Model Context Protocol)](https://modelcontextprotocol.io/)**: Protocolo padrão para conectar IAs a sistemas externos.
  - Utiliza `fastmcp` para definição rápida de ferramentas.
- **Starlette / SSE-Starlette**: Para suporte a Server-Sent Events (SSE), método de transporte utilizado pelo MCP.
- **Uvicorn**: Servidor ASGI para rodar a aplicação.
- **Requests**: Para comunicação com a API do Portainer.
- **Docker & Docker Compose**: Para orquestração e deploy.

## 🛠️ Configurações Necessárias

O projeto utiliza variáveis de ambiente para configuração.

### Opção 1: Arquivo `.env` (Para rodar localmente ou via script)

Crie um arquivo `.env` na raiz do projeto (copie o exemplo se houver ou crie do zero):

```ini
PORTAINER_URL=http://localhost:9000
PORTAINER_API_KEY=sua-api-key-aqui
# Opcional: Variável usada apenas pelo script de verificação
MCP_SERVER_URL=http://localhost:8000/sse
```

### Opção 2: Variáveis de Ambiente do Sistema/Docker

Você pode exportar estas variáveis diretamente no shell ou defini-las no seu orquestrador de containers.

| Variável | Descrição | Obrigatório |
|----------|-----------|-------------|
| `PORTAINER_URL` | URL do seu Portainer (ex: `http://portainer:9000` ou IP público) | Sim |
| `PORTAINER_API_KEY` | Chave de API (Access Token) gerada no Portainer | **Sim** |
| `MCP_SERVER_URL` | URL do servidor MCP (usado apenas pelo `verify_mcp.py`) | Não |

### Como gerar a API Key no Portainer?

1. Acesse seu Portainer.
2. Clique no seu avatar no canto superior direito -> **My account**.
3. Vá até a seção **API keys**.
4. Clique em **Add access token**, dê um nome (ex: "MCP-Agent") e copie a chave gerada.

## 📦 Como Rodar

### Opção 1: Via Docker Compose (Recomendado)

1. Copie o arquivo de exemplo:

   ```bash
   cp docker-compose.example.yml docker-compose.yml
   ```

2. Edite o `docker-compose.yml` e insira suas credenciais.
3. Suba o container:

   ```bash
   docker-compose up -d
   ```

### Opção 2: Rodando Localmente (Python)

1. Crie um ambiente virtual e instale as dependências:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # .venv\Scripts\activate   # Windows
   pip install -r requirements.txt
   ```

2. Certifique-se de que o arquivo `.env` está configurado corretamente.
3. Rode o servidor:

   ```bash
   python server.py
   ```

O servidor iniciará na porta `8000`.

## 🤖 Como Configurar o MCP no MCP Server (Cliente)

Para conectar seu Agente (ex: Antigravity, Claude Desktop) a este servidor MCP, você deve configurar uma conexão via **SSE (Server-Sent Events)**.

### Configuração no Cliente (Agent)

1. **Tipo de Conexão (Transport):** SSE (Server-Sent Events)
2. **URL do Servidor:** `http://<SEU-IP-OU-DOMINIO>:8000/sse`

> **Nota:** Certifique-se de que a porta `8000` está liberada no firewall do servidor onde o Portainer MCP está rodando.

### Exemplo de Configuração (JSON)

Se estiver editando um arquivo de configuração manual (como `claude_desktop_config.json` ou `mcp_config.json`):

```json
{
  "mcpServers": {
    "portainer-mcp": {
      "command": "", 
      "url": "http://127.0.0.1:8000/sse",
      "transport": "sse" 
    }
  }
}
```

*(Nota: Alguns clientes usam `command` para stdio, mas para SSE você usa a `url`)*.

---

## 🧪 Verificando a Instalação

O projeto inclui um script de verificação `verify_mcp.py` para testar se o servidor está respondendo corretamente.

1. Configure a variável `MCP_SERVER_URL` no seu arquivo `.env` (ou exporte-a no terminal).
2. Execute o script:

```bash
python verify_mcp.py
# Ou opcionalmente passando a URL direta:
# python verify_mcp.py http://localhost:8000/sse
```
