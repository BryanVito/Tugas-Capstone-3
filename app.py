
import os
import sys
import time
import uuid

import streamlit as st

APP_FOLDER = os.path.dirname(os.path.abspath(__file__))
os.chdir(APP_FOLDER)
if APP_FOLDER not in sys.path:
    sys.path.insert(0, APP_FOLDER)

st.set_page_config(page_title="Capstone Chatbot", page_icon="🎬", layout="centered")

REQUIRED_KEYS = [
    "OPENAI_API_KEY",
    "QDRANT_URL",
    "QDRANT_API_KEY",
    "LANGFUSE_PUBLIC_KEY",
    "LANGFUSE_SECRET_KEY",
]
OPTIONAL_KEYS = ["OPENAI_BASE_URL", "LANGFUSE_HOST"]


def bridge_secrets_to_env():
    """Memindahkan kunci dari Streamlit secrets (di Streamlit Cloud: menu Settings > Secrets)
    ke os.environ, karena config.py membaca kunci lewat os.getenv.
    HARUS dijalankan SEBELUM 'import config'.
    Di laptop tanpa file .streamlit/secrets.toml, bagian ini dilewati dan config.py membaca file .env."""
    try:
        for key in REQUIRED_KEYS + OPTIONAL_KEYS:
            if key in st.secrets:
                value = str(st.secrets[key]).strip()
                if value != "":
                    os.environ[key] = value
    except Exception:
        pass 


bridge_secrets_to_env()


def find_missing_keys():
    missing = []
    for key in REQUIRED_KEYS:
        value = os.getenv(key)
        if value is None or value.strip() == "" or value.startswith("isi_dengan"):
            missing.append(key)
    return missing


import config 

missing_keys = find_missing_keys()
if missing_keys:
    st.title("🎬 Capstone Chatbot")
    st.error("Kunci berikut belum diisi: " + ", ".join(missing_keys))
    st.markdown(
        "- **Di laptop:** isi file `.env` (salin dari `.env.example`).\n"
        "- **Di Streamlit Cloud:** buka *Manage app > Settings > Secrets*, lalu isi kunci dengan format TOML "
        "(lihat contoh di `.streamlit/secrets.toml.example`)."
    )
    st.stop()

if not os.path.exists(config.IMDB_DB_PATH):
    st.title("🎬 Capstone Chatbot")
    st.error("File " + config.IMDB_DB_PATH + " tidak ditemukan.")
    st.markdown(
        "Di laptop: jalankan `python 06_build_imdb_sqlite.py`. "
        "Di GitHub: pastikan file `data/imdb.db` ikut di-upload (jangan masuk .gitignore)."
    )
    st.stop()

from langfuse import get_client 

from chat_service import ask

LANGFUSE_USER_ID = "streamlit-user"

EXAMPLE_QUESTIONS = [
    "Show me the top 3 movies by IMDB rating.",
    "Recommend a movie about a thief who enters people's dreams.",
    "Which Christopher Nolan movies are in the list?",
    "What are the highest rated movies about space or time travel?",
]

MAX_OUTPUT_SHOWN = 1500


# Fungsi kecil untuk tampilan

def safe_markdown(text):
    """Tanda $ di st.markdown bisa dianggap rumus matematika (LaTeX) sehingga teks 'US$100 ... US$200'
    tampil rusak. Menulis \\$ membuatnya tampil sebagai tanda dolar biasa."""
    return text.replace("$", "\\$")


def start_new_chat():
    st.session_state.messages = []
    st.session_state.session_id = "streamlit-" + uuid.uuid4().hex[:8]
    st.session_state.total_tokens = 0
    st.session_state.question_count = 0


def init_state():
    if "messages" not in st.session_state:
        start_new_chat()


def show_tool_calls(tool_calls):
    if len(tool_calls) == 0:
        st.caption("No agent was called for this question (the supervisor answered directly).")
        return

    for number, call in enumerate(tool_calls, start=1):
        if call["is_handoff"]:
            st.markdown(str(number) + ". **Handoff:** `" + str(call["agent"]) + "` → `" + call["tool"] + "`")
            continue

        st.markdown(str(number) + ". **" + str(call["agent"]) + "** called `" + call["tool"] + "`")
        arguments = call["arguments"]
        if isinstance(arguments, dict) and "query" in arguments:
            st.code(arguments["query"], language="sql")       
        elif arguments:
            st.json(arguments)                                
        output = call["output"]
        if len(output) > MAX_OUTPUT_SHOWN:
            output = output[:MAX_OUTPUT_SHOWN] + "\n... (cut for display)"
        if output.strip() != "":
            st.caption("Result:")
            st.code(output, language="text")


def show_history(history_sent):
    st.caption(
        "Messages sent to the chatbot together with this question "
        "(only the last " + str(config.CHAT_HISTORY_TURNS) + " turns are sent)."
    )
    if len(history_sent) == 0:
        st.write("No previous messages. This was the first question of the chat.")
        return
    for item in history_sent:
        if item["role"] == "user":
            st.markdown("**You:** " + safe_markdown(item["content"]))
        else:
            st.markdown("**Assistant:** " + safe_markdown(item["content"]))


def show_usage(usage, seconds):
    col1, col2, col3 = st.columns(3)
    col1.metric("Input tokens", usage["input_tokens"])
    col2.metric("Output tokens", usage["output_tokens"])
    col3.metric("Total tokens", usage["total_tokens"])
    col4, col5 = st.columns(2)
    col4.metric("LLM calls", usage["llm_calls"])
    col5.metric("Time (seconds)", seconds)
    st.caption("Counted over all LLM calls: supervisor + specialist agents.")


def show_details(details):
    with st.expander("Tool Calls"):
        show_tool_calls(details["tool_calls"])
    with st.expander("History Chat"):
        show_history(details["history_sent"])
    with st.expander("Usage Details"):
        show_usage(details["usage"], details["seconds"])


def show_message(message):
    with st.chat_message(message["role"]):
        st.markdown(safe_markdown(message["content"]))
        if message["role"] == "assistant" and "details" in message:
            show_details(message["details"])



#page

init_state()

with st.sidebar:
    st.header("Capstone Chatbot")
    st.write("Ask about the **IMDB Top 1000 movies**: facts and numbers (SQL agent) or plots and themes (RAG agent).")
    if st.button("🗑️ New chat", use_container_width=True):
        start_new_chat()
        st.rerun()

    st.subheader("Try an example")
    clicked_example = None
    for example_number, example in enumerate(EXAMPLE_QUESTIONS):
        if st.button(example, key="example_" + str(example_number), use_container_width=True):
            clicked_example = example

    st.subheader("This chat")
    st.caption("Langfuse session: " + st.session_state.session_id)
    st.caption("Questions: " + str(st.session_state.question_count))
    st.caption("Total tokens: " + str(st.session_state.total_tokens))

st.title("🎬 IMDB Movie Chatbot")
st.caption("Multi-agent chatbot: supervisor → film_stats_expert (SQL) and film_search_expert (RAG with Qdrant).")

for old_message in st.session_state.messages:
    show_message(old_message)

typed_question = st.chat_input("Ask about movies...")
question = clicked_example or typed_question

if question:
    max_messages = config.CHAT_HISTORY_TURNS * 2
    history_sent = [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages[-max_messages:]
    ]

    with st.chat_message("user"):
        st.markdown(safe_markdown(question))

    with st.chat_message("assistant"):
        started = time.time()
        try:
            with st.spinner("The agents are working..."):
                result = ask(
                    question,
                    history_sent,
                    session_id=st.session_state.session_id,
                    user_id=LANGFUSE_USER_ID,
                    tags=["streamlit", "supervisor"],
                )
            get_client().flush()  
        except Exception as error:
            st.error(
                "Sorry, something went wrong while answering. Please try again in a moment.\n\n"
                + type(error).__name__ + ": " + str(error)[:300]
            )
            st.stop()

        seconds = round(time.time() - started, 1)
        answer = result["answer"] or "Sorry, I could not produce an answer. Please try rephrasing your question."
        st.markdown(safe_markdown(answer))

        details = {
            "tool_calls": result["tool_calls"],
            "history_sent": history_sent,
            "usage": result["usage"],
            "seconds": seconds,
        }
        show_details(details)

    st.session_state.messages.append({"role": "user", "content": question})
    st.session_state.messages.append({"role": "assistant", "content": answer, "details": details})
    st.session_state.question_count += 1
    st.session_state.total_tokens += result["usage"]["total_tokens"]
    st.rerun()
