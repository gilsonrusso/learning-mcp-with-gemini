import asyncio
import os

from fastmcp import Client
from fastmcp.client.auth import BearerAuth
from fastmcp.client.transports import StreamableHttpTransport
from langchain_core.messages import HumanMessage
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

# A nova importação do LangGraph que substitui o AgentExecutor
from langgraph.prebuilt import create_react_agent


async def main():
    """
    Cliente MCP refatorado usando fastmcp.Client, LangChain, Ollama e LANGGRAPH.
    Conecta-se ao servidor Pet Store e usa ferramentas do MCP.
    """

    # 1. Configuração do LLM (Ollama)
    llm = ChatOllama(
        model="qwen2.5-coder:7b",
        temperature=0,
    )

    # 2. Configuração do Cliente FastMCP
    server_url = "http://localhost:8000/mcp"
    transport = StreamableHttpTransport(server_url)

    # Adicionando o cabeçalho Authorization
    client = Client(
        transport=transport, auth=BearerAuth(os.getenv("TOKEN_MCP_CLIENTE"))
    )

    print(f"Conectando ao servidor MCP em {server_url}...")

    # 3. Bloco de contexto assíncrono para o cliente
    async with client:
        print("Conexão com FastMCP estabelecida!")
        await client.ping()

        # 4. Listar ferramentas e converter para LangChain
        tools = await client.list_tools()
        resources = await client.list_resources()
        prompts = await client.list_prompts()

        print(f"Ferramentas PetStore encontradas: {[t.name for t in tools]}")

        # Converte as ferramentas do MCP para o padrão do LangChain
        langchain_tools = await load_mcp_tools(client.session)

        # 5. Criação do Agente com LangGraph
        # Criamos o agente de forma limpa, sem o state_modifier que estava causando o erro
        agent = create_react_agent(model=llm, tools=langchain_tools)

        # 6. Loop de interação via terminal
        print("\n--- Cliente Interativo (LangGraph) Pronto ---")
        print("Digite suas perguntas (ou 'sair' para encerrar):")

        instrucoes_sistema = "Você é um assistente útil e amigável. Use as ferramentas disponíveis quando necessário para responder às perguntas do usuário."

        while True:
            try:
                query = input("\nVocê: ").strip()

                if not query:
                    continue

                if query.lower() in ["sair", "exit", "quit"]:
                    print("Encerrando cliente...")
                    break

                print("Processando...")

                # Passamos a instrução do sistema explicitamente como a primeira mensagem do estado
                estado_inicial = {
                    "messages": [
                        SystemMessage(content=instrucoes_sistema),
                        HumanMessage(content=query),
                    ]
                }

                response = await agent.ainvoke(estado_inicial)

                mensagem_final = response["messages"][-1].content
                print(f"\nAssistente: {mensagem_final} \n")

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
