# Capstone Project Module 3 (dataset: IMDB Top 1000)

Chatbot multi-agent tentang 1000 film IMDB teratas. Satu dataset, dua cara menjawab:
- `film_search_expert`: mencari film berdasarkan cerita, tema, "film mirip ...", memakai RAG tool `search_movies` (Qdrant Cloud)
- `film_stats_expert`: menjawab fact dan numbers (rating, tahun, sutradara, jumlah, peringkat), memakai SQL ke SQLite
- `supervisor`: membaca pertanyaan lalu menyerahkannya ke agent yang tepat (atau ke keduanya)
- Semua prompt disimpan di Langfuse, setiap pertanyaan tercatat (tracing) di Langfuse
- Aplikasi web Streamlit (`app.py`) dengan 3 kotak lipat: Tool Calls, History Chat, Usage Details

## Urutan menjalankan (dari folder utama proyek)

1. `python 01_test_connection.py`            -> tes OpenAI, Qdrant, Langfuse
2. `python 02_explore_data.py`               -> lihat isi dataset
3. `python 03_check_documents.py`            -> lihat satu film jadi satu chunk
4. `python 04_upload_movies_to_qdrant.py`    -> upload 1000 film ke Qdrant (koleksi `imdb_movies`)
5. `python 05_test_search.py`                -> tes pencarian dan pilih threshold
6. `python movie_search_tool.py`             -> tes RAG tool

7.  `python 06_build_imdb_sqlite.py`          -> CSV IMDB menjadi database data/imdb.db
8.  `python 07_test_sql_tools.py`             -> tes alat SQL
9.  `python 08_upload_prompts_to_langfuse.py` -> unggah 3 prompt ke Langfuse
10. `python 09_test_film_agent.py`            -> tes agent statistik (SQL)
11. `python 10_test_film_search_agent.py`     -> tes agent pencarian (RAG)
12. `python 11_test_supervisor.py`            -> tes supervisor + riwayat chat
13. `python 12_chat_cli.py`                   -> chatbot di terminal

14. `streamlit run app.py`                   -> aplikasi web

## Peta file

| File | Fungsi |
| --- | --- |
| `config.py` | semua pengaturan dan pembaca file .env |
| `models.py` | membuat LLM dan embeddings |
| `imdb_data.py` | membersihkan data IMDB |
| `movie_documents.py` | satu film menjadi satu Document untuk Qdrant |
| `movie_search_tool.py` | RAG tool `search_movies` |
| `sql_tools.py` | tool SQL (`get_db_schema_tool`, `execute_query_tool`), database read-only |
| `prompts.py` | mengambil prompt dari Langfuse |
| `film_search_agent.py` | agent pencarian film (RAG) |
| `film_agent.py` | agent statistik film (SQL) |
| `supervisor.py` | supervisor yang membagi tugas |
| `tracing.py` | menyambungkan ke Langfuse (CallbackHandler) |
| `chat_service.py` | riwayat chat, jawaban, tool calls, jumlah token |
| `app.py` | aplikasi web Streamlit |
| `.streamlit/secrets.toml.example` | contoh isi menu Secrets di Streamlit Cloud |

