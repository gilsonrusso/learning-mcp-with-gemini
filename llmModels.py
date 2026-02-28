import os

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_ollama import ChatOllama, OllamaEmbeddings


def get_llm_model(model_name: str):
    if model_name == "ollama":
        return ChatOllama(
            model=model_name,
            temperature=0.7,
            timeout=30,
            max_tokens=1000,
            max_retries=6,  # Default; increase for unreliable networks"
        )
    elif model_name == "gemini":
        return ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            temperature=0.1,
            api_key=os.getenv("GOOGLE_API_KEY"),
        )
    else:
        raise ValueError(f"Modelo {model_name} não suportado.")


def get_embedding_model(model_name: str):
    return OllamaEmbeddings(model=model_name)
