import asyncio
import os

from dotenv import load_dotenv

load_dotenv()

from fastmcp import Client
from fastmcp.client.auth import BearerAuth
from fastmcp.client.transports import StreamableHttpTransport
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_mcp_adapters.tools import load_mcp_tools

# Importação correta do agente
from langgraph.prebuilt import create_react_agent
from llmModels import get_llm_model


async def main():
    """
    Cliente MCP refatorado usando fastmcp.Client, LangChain, Ollama e LANGGRAPH.
    Conecta-se ao servidor Pet Store e usa ferramentas do MCP.
    """

    # 1. Configuração do LLM
    llm = get_llm_model("gemini")

    # 2. Configuração do Cliente FastMCP único (Porta 8000)
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

        print(f"Ferramentas encontradas: {[t.name for t in tools]}")

        # Converte as ferramentas do MCP para o padrão do LangChain
        raw_tools = await load_mcp_tools(client.session)

        # WORKAROUND PARA O GEMINI:
        # A integração do LangChain com a API nova do Gemini v2 recusa schemas JSON que contêm
        # a flag "additionalProperties" no nível raiz das propriedades. Precisamos limpar isso
        # recriando as ferramentas de forma controlada.
        from langchain_core.tools import StructuredTool
        from pydantic import BaseModel, ConfigDict, Field

        class BuscaDocSchema(BaseModel):
            model_config = ConfigDict(extra="forbid")
            duvida: str = Field(
                description="A dúvida ou termo para pesquisar na base de conhecimento."
            )

        langchain_tools = []
        for t in raw_tools:
            if t.name == "buscar_documentacao":
                # Recriamos a ferramenta manualmente usando o Func do tool original e nosso Schema Pydantic limpo
                clean_tool = StructuredTool.from_function(
                    func=t.invoke,  # chamamos o invoke do mcp adaptado
                    coroutine=t.ainvoke,  # chamamos a versão async
                    name=t.name,
                    description=t.description,
                    args_schema=BuscaDocSchema,
                )
                langchain_tools.append(clean_tool)
            else:
                langchain_tools.append(t)

        print(f"\n[DEBUG] Descrição das ferramentas carregadas:")
        for t in langchain_tools:
            print(f"- {t.name}: {t.description}")
        print("-" * 40 + "\n")

        # 5. Criação do Agente com LangGraph
        agent = create_react_agent(model=llm, tools=langchain_tools)

        # 6. Loop de interação via terminal
        print("\n--- Cliente Interativo (LangGraph) Pronto ---")
        print("Digite suas perguntas (ou 'sair' para encerrar):")

        instrucoes_sistema = (
            "Você é um assistente útil e amigável. "
            "Para responder às perguntas do usuário, você DEVE primeiramente buscar na sua base de dados "
            "usando a ferramenta `buscar_documentacao`. Nunca diga que não tem informações sem antes "
            "executar uma busca na ferramenta. Retorne o texto sempre em formato Markdown."
        )

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

                # O LangChain v0.3 com Gemini às vezes retorna o content como uma lista de dicts
                if isinstance(mensagem_final, list):
                    partes = [
                        bloco.get("text", "")
                        for bloco in mensagem_final
                        if isinstance(bloco, dict) and bloco.get("type") == "text"
                    ]
                    if partes:
                        mensagem_final = "".join(partes)
                    else:
                        mensagem_final = str(mensagem_final)

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
