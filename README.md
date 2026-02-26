# Learning MCP with Gemini & Ollama

Este projeto é uma exploração prática do **Model Context Protocol (MCP)** utilizando **FastMCP**, **LangChain** e **Ollama**.

O objetivo é expor uma API externa (Swagger PetStore) como ferramentas de um servidor MCP e consumi-las através de um cliente interativo que utiliza um LLM local.

## 🚀 Tecnologias

- **Python 3.12+**
- **FastMCP**: Framework para criação rápida de servidores e clientes MCP.
- **LangChain**: Orquestração do LLM e integração de ferramentas.
- **Ollama**: Runner de modelos de IA local (utilizando `qwen2.5-coder:7b`).
- **HTTP/SSE**: Transporte utilizado para comunicação entre cliente e servidor.

## 🛠️ Configuração

### 1. Requisitos
Certifique-se de ter o [Ollama](https://ollama.com/) instalado e o modelo baixado:
```bash
ollama pull qwen2.5-coder:7b
```

### 2. Ambiente Virtual
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install langchain-ollama langchain-mcp-adapters mcp httpx fastmcp
```

### 3. Variáveis de Ambiente
Crie um arquivo `.env` (se necessário para a sua API) ou defina o token para o cliente:
```bash
export TOKEN_MCP_CLIENTE="seu_token_aqui"
```

## 🏃 Como Rodar

### Passo 1: Iniciar o Servidor
O servidor carrega a especificação OpenAPI da PetStore e a expõe via MCP.
```bash
fastmcp run servidor.py:mcp --transport http
fastmcp run servidor.py:mcp --transport sse --reload
```

### Passo 2: Iniciar o Cliente Interativo
Em outro terminal:
```bash
python cliente.py
```

## 📂 Estrutura do Projeto

- `servidor.py`: Define o servidor FastMCP que consome a API OpenAPI.
- `cliente.py`: Cliente interativo LangChain + Ollama que utiliza as ferramentas do servidor.
- `.gitignore`: Configurações de exclusão para o Git.

---
Desenvolvido para aprendizado de Model Context Protocol.
