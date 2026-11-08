
import config
from langchain_openai import OpenAIEmbeddings, ChatOpenAI


def get_embeddings():
    if config.OPENAI_BASE_URL:
        return OpenAIEmbeddings(
            model=config.EMBEDDING_MODEL,
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            check_embedding_ctx_length=False,
        )
    return OpenAIEmbeddings(
        model=config.EMBEDDING_MODEL,
        api_key=config.OPENAI_API_KEY,
    )


def get_llm(model_name=None):
    """Membuat LLM. Kalau model_name tidak diisi, dipakai config.LLM_MODEL.
    temperature=0 supaya jawaban stabil."""
    if model_name is None:
        model_name = config.LLM_MODEL

    if config.OPENAI_BASE_URL:
        return ChatOpenAI(
            model=model_name,
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
            temperature=0,
        )
    return ChatOpenAI(
        model=model_name,
        api_key=config.OPENAI_API_KEY,
        temperature=0,
    )
