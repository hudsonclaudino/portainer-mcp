import os
from dotenv import load_dotenv

# Carrega variáveis do arquivo .env (se existir)
load_dotenv()

# Tenta importar as bibliotecas do cliente MCP
try:
    from mcp.client.sse import sse_client
    from mcp.client.session import ClientSession
except ImportError:
    print("Erro: Biblioteca 'mcp' não encontrada ou versão incompatível.")
    print("Instale com: pip install mcp python-dotenv")
    sys.exit(1)

async def main():
    # --- CONFIGURAÇÃO ---
    # Busca a URL da variável de ambiente ou usa um padrão
    DEFAULT_URL = "http://localhost:8000/sse"
    SERVER_URL = os.getenv("MCP_SERVER_URL", DEFAULT_URL)
    
    # Permite sobrescrever via argumento de linha de comando
    if len(sys.argv) > 1:
        SERVER_URL = sys.argv[1]

    print(f"📡 Conectando ao servidor MCP em: {SERVER_URL}")
    print("--------------------------------------------------")

    try:
        async with sse_client(SERVER_URL) as streams:
            async with ClientSession(streams[0], streams[1]) as session:
                # 1. Inicializa Conexão
                await session.initialize()
                print("✅ Conexão inicializada com sucesso!")

                # 2. Lista Ferramentas
                print("\n🔎 Listando ferramentas disponíveis...")
                tools_result = await session.list_tools()
                
                if not tools_result.tools:
                    print("⚠️ Nenhuma ferramenta encontrada.")
                else:
                    for tool in tools_result.tools:
                        print(f"   🔨 {tool.name}: {tool.description}")

                # 3. Executa a ferramenta 'list_stacks'
                print("\n🚀 Executando tool 'list_stacks'...")
                try:
                    result = await session.call_tool("list_stacks")
                    # O resultado vem como uma lista de conteúdos (TextContent, ImageContent, etc)
                    for content in result.content:
                        if content.type == 'text':
                            print(f"\n📄 RESPOSTA:\n{content.text}")
                        else:
                            print(f"\n📦 RESPOSTA ({content.type}): {content}")
                            
                except Exception as e:
                    print(f"❌ Erro ao chamar list_stacks: {str(e)}")

    except Exception as e:
        import traceback
        with open("checking_error.log", "w") as f:
            f.write(f"Error Type: {type(e).__name__}\n")
            f.write(f"Error Message: {str(e)}\n\n")
            traceback.print_exc(file=f)
        
        print(f"\n❌ Erro fatal. Detalhes salvos em checking_error.log")
        print(f"Erro: {str(e)}")

if __name__ == "__main__":
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
