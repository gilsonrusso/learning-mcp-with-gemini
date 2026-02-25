import asyncio
from langchain_ollama import ChatOllama
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerAuth
from langchain_mcp_adapters.tools import load_mcp_tools
import os

async def main():
    """
    Cliente MCP refatorado usando fastmcp.Client, LangChain e Ollama.
    Conecta-se ao servidor Pet Store (via FastMCP no servidor.py).
    """
    
    # 1. Configuração do LLM (Ollama)
    llm = ChatOllama(
        model="qwen2.5-coder:7b",
        temperature=0,
    )

    # 2. Configuração do Cliente FastMCP
    # O servidor está rodando na porta 8000 com transporte HTTP/SSE.
    server_url = "http://localhost:8000/mcp"

    transport = StreamableHttpTransport(
        server_url,
    )
    
    # Adicionando o cabeçalho Authorization conforme solicitado pelo servidor.py
    client = Client(
        transport=transport,
        auth=BearerAuth(os.getenv("TOKEN_MCP_CLIENTE"))
    )

    print(f"Conectando ao servidor MCP em {server_url}...")

    # 3. Bloco de contexto assíncrono para o cliente
    async with client:
        print("Conexão com FastMCP estabelecida!")
        await client.ping()

        # 4. Listar ferramentas e converter para LangChain
        # O client.list_tools() do FastMCP retorna as ferramentas disponíveis
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()
        
        print(f"Ferramentas PetStore encontradas: {[t.name for t in tools]}")
        print(f"Recursos PetStore encontrados: {[r.name for r in resources]}")
        print(f"Prompts PetStore encontrados: {[p.name for p in prompts]}")

        # 5. Configurar o LLM com as ferramentas
        # O load_mcp_tools do adaptador LangChain simplifica a conversão
        langchain_tools = await load_mcp_tools(client.session)
        
        llm_with_tools = llm.bind_tools(langchain_tools)

        # 6. Loop de interação via terminal
        print("\n--- Cliente Interativo Pronto ---")
        print("Digite suas perguntas (ou 'sair' para encerrar):")
        
        while True:
            try:
                query = input("\nVocê: ").strip()
                
                if not query:
                    continue
                
                if query.lower() in ["sair", "exit", "quit"]:
                    print("Encerrando cliente...")
                    break
                
                print("Processando...")
                
                # Chamada ao LLM (usando o método síncrono ou garantindo que o loop asíncrono rode)
                # Como estamos dentro de um `async def main`, usamos `await`
                response = await llm_with_tools.ainvoke(query)
                
                print(f"\nAssistente: {response.content}")
                
                if response.tool_calls:
                    print(f"\n[Ações do Sistema]:")
                    for tool_call in response.tool_calls:
                        print(f"  - Chamando ferramenta: {tool_call['name']}")
                        print(f"    Argumentos: {tool_call['args']}")
                
            except EOFError:
                break
            except Exception as e:
                print(f"Erro no loop: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nSaindo...")
    except Exception as e:
        print(f"\nErro inesperado: {e}")
