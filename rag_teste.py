import os

import dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_ollama import OllamaEmbeddings
from langchain_qdrant import QdrantVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter

from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams

dotenv.load_dotenv()

URL_QDRANT = os.getenv("URL_QDRANT", "http://localhost:6333")
NOME_COLECAO = os.getenv("NOME_COLECAO", "documentacao_teste")
MODEL_EMBEDDING = os.getenv("MODEL_EMBEDDING", "nomic-embed-text:v1.5")

file_path = "./100_historias_infantis.pdf"
loader = PyPDFLoader(file_path)
docs = loader.load()

print(f"::: {docs[0].page_content[:200]}\n")
print(f"::: {docs[0].metadata}\n")
print(f"::: {len(docs)}\n")

text_splitter = RecursiveCharacterTextSplitter(
    length_function=len,  # Função que calcula o tamanho do texto
    is_separator_regex=False,  # Se o separador é uma expressão regular
    chunk_size=1000,  # Tamanho máximo de cada pedaço (em caracteres)
    chunk_overlap=200,  # Quantos caracteres ele pega 'emprestado' do pedaço anterior
    add_start_index=True,
    separators=[
        "\n\n",
        "\n",
        ".",
        " ",
        "",
    ],  # Ordem de preferência para o corte (tenta não quebrar parágrafos, depois frases...)
)

# 2. Dividindo o texto
all_splits = text_splitter.split_documents(docs)
print(f"Texto dividido em {len(all_splits)} chunks. Gerando embeddings...")

# 4. Configurando o modelo de Embeddings
# Embeddings são representações numéricas (vetoriais) do texto.
# Aqui usamos o modelo "nomic-embed-text:v1.5", que roda localmente via Ollama.
# É ele que vai converter cada pedaço de texto em uma lista de números (ex: [0.12, -0.45, 0.89...]).
embeddings = OllamaEmbeddings(model=MODEL_EMBEDDING)

# 5. Inicializando o cliente do Qdrant
# O QdrantClient é a ferramenta oficial do Qdrant para conversar com o banco de dados.
# Ele se conecta à URL onde o seu Qdrant está rodando (por padrão: http://localhost:6333)
client = QdrantClient(url=URL_QDRANT)

# 6. Preparando o ambiente (Reset da coleção)
# Antes de adicionar textos novos, verificamos se já existe uma coleção com esse nome.
# Se existir, a gente a deleta para começar do zero com uma "lousa em branco" e não misturar dados.
if client.collection_exists(collection_name=NOME_COLECAO):
    client.delete_collection(collection_name=NOME_COLECAO)

# 7. Criando a coleção no Qdrant
# Uma "coleção" no Qdrant é como se fosse uma tabela de banco de dados, mas otimizada para vetores.
# Aqui precisamos dizer o tamanho do vetor (size=768 é o padrão do nomic-embed) e como
# calcular a proximidade entre os textos (Distance.COSINE é o cálculo matemático mais usado para textos).
# Nota: usamos 'create_collection' em vez de 'recreate_collection' para evitar o aviso de depreciação.
client.create_collection(
    collection_name=NOME_COLECAO,
    vectors_config=VectorParams(size=768, distance=Distance.COSINE),
)

# 8. O VectorStore do LangChain
# Essa classe (QdrantVectorStore) é a "ponte" entre a inteligência do LangChain e o banco Qdrant.
# Entregamos a ela: o modelo que gera os vetores (embeddings), o cliente do banco (client)
# e o local onde isso vai ficar (collection_name).
vectorstore = QdrantVectorStore(
    embedding=embeddings,
    client=client,
    collection_name=NOME_COLECAO,
)

# 9. Adicionando os textos ao banco
# Aqui a mágica acontece! Esse comando pega todos os seus 'pedaços' de texto, envia
# para o Ollama converter em números (embeddings), e salva tudo lá na coleção do Qdrant.
vectorstore.add_documents(documents=all_splits)
print("✅ Tudo salvo no Qdrant com sucesso!\n")

# 10. Fazendo a busca (Retrieval)
# É a hora da "Pesquisa Semântica". Você manda uma pergunta ("O que é MCP?").
# Essa pergunta também é convertida em um vetor, e o Qdrant procura no banco
# quais vetores (documentos) estão matematicamente mais 'próximos' (Distance.COSINE) do vetor da pergunta.
# O 'k=2' diz para ele retornar os 2 melhores resultados.
print("🔍 Fazendo uma busca por similaridade...")
resultados = vectorstore.similarity_search("Quem usava um macacão azul?", k=2)

print("\n--- Resultados Encontrados ---")
for i, doc in enumerate(resultados):
    print(f"Documento {i+1}:")
    print(doc.page_content)
    print("-" * 20)
