import httpx
from fastmcp import FastMCP
from fastmcp.server.dependencies import get_http_headers
from fastmcp.server.providers.openapi import RouteMap, MCPType

# 1. Criamos um interceptador para o httpx
class TokenPassthroughAuth(httpx.Auth):
    def auth_flow(self, request):
        # Captura os cabeçalhos da requisição HTTP atual do usuário (LangChain/Ollama)
        headers = get_http_headers() or {}
        
        # Procura o token enviado pelo cliente MCP
        # O cabeçalho geralmente chega em minúsculo no dicionário
        auth_header = headers.get("authorization")
        
        # Se o cliente enviou o token, repassamos ele para a requisição da sua API
        if auth_header:
            print(f"DEBUG: Token recebido do MCP: {auth_header}")
            request.headers["Authorization"] = auth_header
            
        yield request

# 2. Configurando o Cliente HTTP sem token fixo
# Em vez de passar um headers={"Authorization": ...} fixo, usamos nossa classe dinâmica
api_client = httpx.AsyncClient(
    base_url="https://petstore3.swagger.io/api/v3",
    auth=TokenPassthroughAuth(),
    timeout=30.0 
)

# 3. Carregando a Especificação OpenAPI
openapi_spec = httpx.get("https://petstore3.swagger.io/api/v3/openapi.json").json()

# 3.1. Definindo Mapeamento Semântico
# Mapeia todas as rotas como ferramentas (TOOLS) conforme solicitado
semantic_maps = [
    RouteMap(mcp_type=MCPType.TOOL),
]

# 4. Criando o Servidor FastMCP
mcp = FastMCP.from_openapi(
    openapi_spec=openapi_spec,
    client=api_client, 
    name="Pet Store API",
    instructions="Servidor para gerenciar dados de RH e KPIs.",
    route_maps=semantic_maps # Added route_maps parameter
)


@mcp.resource("system://pet_store_manager")
def pet_store_manager():
    """Instruções para o assistente atuar como um gerente especializado na Pet Store."""
    return (
        "Você é um gerente especializado da Pet Store. "
        "Siga estas diretrizes ao responder:\n"
        "1. Seja profissional mas amigável (tom de 'apaixonado por pets').\n"
        "2. Se for uma dúvida técnica sobre a API, explique de forma clara.\n"
        "3. Sempre que possível, mencione boas práticas de cuidado com os animais.\n"
        "4. A resposta DEVE ser formatada obrigatoriamente em Markdown, usando títulos, tabelas e negritos para melhor leitura.\n"
        "5. IMPORTANTE: Sempre encerre sua resposta com a assinatura: '> *Atenciosamente, Gerente da Pet Store 🐾*'"
    )

if __name__ == "__main__":
    # É obrigatório rodar usando um transporte HTTP (e não STDIO) para que o fluxo
    # de cabeçalhos HTTP (Bearer Token) funcione entre o cliente e o servidor FastMCP.
    mcp.run(transport="http", port=8000)