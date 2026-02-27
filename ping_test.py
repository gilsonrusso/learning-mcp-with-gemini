import asyncio
import os
from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport
from fastmcp.client.auth import BearerAuth


async def main():
    transport = StreamableHttpTransport("http://localhost:8000/mcp")
    client = Client(
        transport=transport, auth=BearerAuth(os.getenv("TOKEN_MCP_CLIENTE"))
    )

    print("Iniciando conexão...")
    async with client:
        print("Conectado! Fazendo ping...")
        await client.ping()
        print("Ping OK!")


if __name__ == "__main__":
    asyncio.run(main())
