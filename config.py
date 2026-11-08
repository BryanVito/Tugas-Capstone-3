
import os
import sys
from dotenv import load_dotenv


load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
LANGFUSE_PUBLIC_KEY = os.getenv("LANGFUSE_PUBLIC_KEY")
LANGFUSE_SECRET_KEY = os.getenv("LANGFUSE_SECRET_KEY")
LANGFUSE_HOST = os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")

OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")

EMBEDDING_SIZE = 1536

if OPENAI_BASE_URL:
    EMBEDDING_MODEL = "openai/text-embedding-3-small"
    LLM_MODEL = "openai/gpt-4o-mini"
else:
    EMBEDDING_MODEL = "text-embedding-3-small"
    LLM_MODEL = "gpt-4o-mini"


MOVIE_COLLECTION_NAME = "imdb_movies"
SCORE_THRESHOLD = 0.25
TOP_K = 5   

IMDB_CSV_PATH = os.path.join("data", "imdb_top_1000.csv")
IMDB_DB_PATH = os.path.join("data", "imdb.db")  

MODEL_PREFIX = "openai/" if OPENAI_BASE_URL else ""
SUPERVISOR_LLM_MODEL = MODEL_PREFIX + "gpt-4.1"
AGENT_LLM_MODEL = MODEL_PREFIX + "gpt-4.1-mini"

SQL_TOP_K = 5              
CHAT_HISTORY_TURNS = 5    

PROMPT_SUPERVISOR = "capstone-supervisor"
PROMPT_FILM_AGENT = "capstone-film-agent"
PROMPT_FILM_SEARCH_AGENT = "capstone-film-search-agent"
PROMPT_LABEL = "production"  


def check_keys(list_of_key_names):
    """Cek apakah kunci yang dibutuhkan sudah terisi di file .env.
    Kalau ada yang kosong, tulis namanya lalu hentikan program."""
    missing_keys = []
    for key_name in list_of_key_names:
        value = os.getenv(key_name)
        if value is None or value == "" or value.startswith("isi_dengan"):
            missing_keys.append(key_name)

    if len(missing_keys) > 0:
        print("Kunci berikut belum diisi di file .env:")
        for key_name in missing_keys:
            print("  -", key_name)
        print("Buka file .env, isi kuncinya, simpan, lalu jalankan lagi.")
        sys.exit(1)
