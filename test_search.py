import os
import dotenv
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient

dotenv.load_dotenv()
embed = OllamaEmbeddings(model=os.getenv("MODEL_EMBEDDING", "nomic-embed-text:v1.5"))
client = QdrantClient(url=os.getenv("URL_QDRANT", "http://localhost:6333"))
vector_store = QdrantVectorStore(
    client=client,
    collection_name=os.getenv("NOME_COLECAO", "documentacao_teste"),
    embedding=embed,
)

print("Testando busca de macacão azul no Qdrant (K=5):")
q1 = vector_store.similarity_search("quem usava macacão azul?", k=5)
for i, doc in enumerate(q1):
    print(f"--- Doc {i+1} ---")
    print(doc.page_content)

print("\n\nTestando busca mais específica:")
q2 = vector_store.similarity_search("macacão azul", k=5)
for i, doc in enumerate(q2):
    print(f"--- Doc {i+1} ---")
    print(doc.page_content)
