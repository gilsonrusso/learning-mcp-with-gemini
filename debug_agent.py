import asyncio
import os
from langchain_ollama import ChatOllama
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerAuth
from langchain_mcp_adapters.tools import load_mcp_tools
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage


async def main():
    llm = ChatOllama(model="qwen2.5-coder:7b", temperature=0)
    transport = StreamableHttpTransport("http://localhost:8000/mcp")
    client = Client(
        transport=transport, auth=BearerAuth(os.getenv("TOKEN_MCP_CLIENTE"))
    )

    async with client:
        await client.ping()
        tools = await load_mcp_tools(client.session)
        agent = create_react_agent(llm, tools)

        print("Enviando requisição...")
        async for chunk in agent.astream(
            {"messages": [HumanMessage(content="oque é mcp?")]}, stream_mode="values"
        ):
            msg = chunk["messages"][-1]
            print(f"Tipo: {type(msg).__name__} | Conteúdo: {msg.content}")
            if hasattr(msg, "tool_calls") and msg.tool_calls:
                print(f"Tool calls: {msg.tool_calls}")


if __name__ == "__main__":
    asyncio.run(main())
