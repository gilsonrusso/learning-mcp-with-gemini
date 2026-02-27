import asyncio
import os
from langchain_ollama import ChatOllama
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerAuth
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate


async def main():
    llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0)
    transport = StreamableHttpTransport("http://localhost:8000/mcp")
    client = Client(
        transport=transport, auth=BearerAuth(os.getenv("TOKEN_MCP_CLIENTE"))
    )

    async with client:
        await client.ping()
        tools = await load_mcp_tools(client.session)
        print("Tools loaded:", [t.name for t in tools])

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", "Você é um assistente útil."),
                ("human", "{input}"),
                ("placeholder", "{agent_scratchpad}"),
            ]
        )

        agent = create_tool_calling_agent(llm, tools, prompt)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        print("Iniciando ainvoke...")
        res = await agent_executor.ainvoke({"input": "oque é mcp?"})
        print("Resultado:", res)


if __name__ == "__main__":
    asyncio.run(main())
