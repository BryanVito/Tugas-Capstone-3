
import sqlite3
from pathlib import Path

from langchain_community.utilities import SQLDatabase
from langchain_core.tools import tool
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool

import config

MAX_OUTPUT_CHARS = 6000  

_database = None 


def _open_read_only():
    """Membuka file imdb.db dengan mode=ro (read only)."""
    db_file = Path(config.IMDB_DB_PATH).resolve()
    if not db_file.exists():
        raise FileNotFoundError(
            "File " + str(db_file) + " tidak ditemukan. Jalankan dulu: python 06_build_imdb_sqlite.py"
        )
    return sqlite3.connect(db_file.as_uri() + "?mode=ro", uri=True, check_same_thread=False)


def get_db():
    """Mengembalikan objek SQLDatabase LangChain (dibuat sekali, dipakai ulang)."""
    global _database
    if _database is None:
        engine = create_engine("sqlite://", creator=_open_read_only, poolclass=StaticPool)
        _database = SQLDatabase(engine)
    return _database


def check_select_only(query):
    """Mengembalikan None kalau query aman. Kalau tidak aman, mengembalikan tulisan alasannya."""
    cleaned = query.strip()
    while cleaned.endswith(";"):
        cleaned = cleaned[:-1].strip()

    if cleaned == "":
        return "The query is empty."
    if ";" in cleaned:
        return "Only one SQL statement is allowed per call."

    first_word = cleaned.split()[0].lower()
    if first_word not in ("select", "with"):
        return "Only SELECT queries are allowed. This database is read-only."
    return None


@tool
def get_db_schema_tool() -> str:
    """Get the schema of the movie database: table names, columns, types, keys, and 3 sample rows per table.
    Always call this first, before writing any SQL query."""
    schema_text = get_db().get_table_info()
    reminder = (
        "\n\nNEXT STEP: write a SELECT query and run it with execute_query_tool. "
        "Do not answer from your own knowledge. The answer must come from the query result."
    )
    return schema_text + reminder


@tool
def execute_query_tool(query: str) -> str:
    """Execute one read-only SQL SELECT query on the movie database and return the result rows.
    If the query is wrong, an error message is returned, so you can fix the query and try again."""
    problem = check_select_only(query)
    if problem is not None:
        return "Error: " + problem

    try:
        result = get_db().run(query)
    except Exception as error:
        return "Error: " + str(error)

    result = str(result)
    if result.strip() == "":
        return "The query ran successfully but returned no rows."
    if len(result) > MAX_OUTPUT_CHARS:
        result = result[:MAX_OUTPUT_CHARS] + "\n... (result truncated, add LIMIT or select fewer columns)"
    return result


SQL_TOOLS = [get_db_schema_tool, execute_query_tool]
