import asyncio
import os

import nest_asyncio

# Permite rodar o loop assíncrono durante a inicialização do módulo
# (Necessário para conectar e buscar as ferramentas MCP antes do LangGraph iniciar as rotas REST)
nest_asyncio.apply()

from fastmcp import Client
from fastmcp.client.auth import BearerAuth
from fastmcp.client.transports import StreamableHttpTransport
from langchain.agents import create_agent
from langchain_mcp_adapters.tools import load_mcp_tools

from llmModels import get_llm_model

# Configuração do LLM
llm = get_llm_model("gemini")


async def setup_mcp_tools():
    """Conecta ao FastMCP Server e converte as ferramentas do servidor em ferramentas do LangChain."""
    server_url = "http://localhost:8000/mcp"
    transport = StreamableHttpTransport(server_url)

    token = os.getenv("TOKEN_MCP_CLIENTE", "dummy_token")
    client = Client(transport=transport, auth=BearerAuth(token))

    print("Conectando ao FastMCP...")
    # # Mantém a conexão aberta para uso contínuo pelo LangGraph
    await client.__aenter__()
    print("Conexão estabelecida!")

    langchain_tools = await load_mcp_tools(client.session)
    print(f"[{len(langchain_tools)}] Ferramentas MCP carregadas com sucesso.")
    return langchain_tools


# Tenta carregar as ferramentas no escopo global
try:
    loop = asyncio.get_event_loop()
    mcp_tools = loop.run_until_complete(setup_mcp_tools())
except RuntimeError:
    mcp_tools = asyncio.run(setup_mcp_tools())

instrucoes_sistema = (
    "Você é um assistente útil e amigável. "
    "Use as ferramentas disponíveis quando necessário para responder às perguntas do usuário de forma clara e objetiva."
)

# A variável 'graph' é obrigatória! É isso que o LangGraph Server espera encontrar.
graph = create_agent(model=llm, tools=mcp_tools)
