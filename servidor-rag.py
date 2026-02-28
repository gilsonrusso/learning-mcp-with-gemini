import os

import dotenv
from fastmcp import FastMCP

# RAG
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

dotenv.load_dotenv()

MODEL_EMBEDDING = os.getenv("MODEL_EMBEDDING", "nomic-embed-text:v1.5")
URL_QDRANT = os.getenv("URL_QDRANT", "http://localhost:6333")
NOME_COLECAO = os.getenv("NOME_COLECAO", "documentacao_teste")

# Configura o modelo de embeddings (o mesmo que usamos para salvar)
embeddings = OllamaEmbeddings(model=MODEL_EMBEDDING)

# Conecta ao Qdrant que está rodando no Docker
qdrant_client = QdrantClient(url=URL_QDRANT)

# Cria o Vector Store (a "memória")
vector_store = QdrantVectorStore(
    client=qdrant_client,  # Cliente do Qdrant
    collection_name=NOME_COLECAO,  # Nome da coleção (tabela)
    embedding=embeddings,  # Modelo de embeddings
)


# ==========================================
# Criando o Servidor FastMCP para o RAG
# ==========================================
mcp = FastMCP(
    name="RAG Documentação",
    instructions="Servidor especializado em buscar informações na base de conhecimento interna.",
)


@mcp.tool()
def buscar_documentacao(duvida: str) -> str:
    """
    Busca informações na base de conhecimento vetorial (RAG).
    A base de dados contém documentos variados, incluindo histórias infantis.
    Use esta ferramenta SEMPRE que o usuário fizer uma pergunta sobre histórias, personagens, ou necessitar de uma busca na base de dados de textos.
    """
    print(f"\n[MCP Server RAG] 🔍 Buscando no RAG por: '{duvida}'")

    # Faz a busca vetorial aumentando K para retornar os 6 melhores matches
    resultados = vector_store.similarity_search(duvida, k=6)

    if not resultados:
        return "Nenhuma informação relevante foi encontrada na documentação."

    # Formata os pedaços encontrados em um texto único para o LLM ler
    textos = [f"- {doc.page_content}" for doc in resultados]
    resposta_formatada = (
        "Trechos relevantes encontrados na documentação:\n" + "\n".join(textos)
    )

    return resposta_formatada


@mcp.resource("system://rag_manager")
def rag_manager():
    """Instruções para o assistente utilizar a base de dados."""
    return (
        "Você é um assistente especialista na base de conhecimentos vetorial (RAG). "
        "Siga estas diretrizes ao responder:\n"
        "1. A base de dados pode conter informações variadas, como histórias, contos ou dados de conhecimento gerais.\n"
        "2. Baseie-se e confie nas informações retornadas pela ferramenta `buscar_documentacao` para responder.\n"
        "3. A resposta DEVE ser formatada obrigatoriamente em Markdown para melhor leitura.\n"
    )


if __name__ == "__main__":
    # Roda o RAG na porta 8001 para não conflitar com a Pet Store na porta 8000
    mcp.run(transport="http", port=8000)
