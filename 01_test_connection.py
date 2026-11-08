
import config
from models import get_embeddings, get_llm
from qdrant_client import QdrantClient
from langfuse import get_client


config.check_keys([
    "OPENAI_API_KEY",
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
])

print("=== Tes 1: OpenAI ===")
try:
    embeddings = get_embeddings()
    vector = embeddings.embed_query("ini tes embedding")
    print("Embedding berhasil. Panjang vektor =", len(vector))
    if len(vector) != config.EMBEDDING_SIZE:
        print("REMINDER: panjang vektor tidak sama dengan EMBEDDING_SIZE di config.py!")

    llm = get_llm()
    answer = llm.invoke("Jawab dengan satu kata saja misalnya: Halo?")
    print("LLM berhasil menjawab:", answer.content)
except Exception as error:
    print("OpenAI error:", error)
    print("Petunjuk: check OPENAI_API_KEY, pastiin account OpenAI punya saldo (credit),")
    print("dan pastiin komputer terhubung ke internet.")

print()
print("=== Tes 2: Qdrant Cloud ===")
try:
    client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY)
    collections = client.get_collections()
    print("Qdrant berhasil. Jumlah collection sekarang =", len(collections.collections))
    for one_collection in collections.collections:
        print("  -", one_collection.name)
except Exception as error:
    print("Qdrant error:", error)
    print("Petunjuk: check QDRANT_URL (harus lengkap, diawali https://) dan QDRANT_API_KEY.")

print()
print("=== Tes 3: Langfuse ===")
try:
    langfuse = get_client()   # otomatis membaca LANGFUSE_... dari file .env
    if langfuse.auth_check():
        print("Langfuse berhasil. key benar.")
    else:
        print("Langfuse error: key salah atau LANGFUSE_HOST tidak sesuai dengan region account.")
except Exception as error:
    print("Langfuse error:", error)

print()
print("Selesai")
