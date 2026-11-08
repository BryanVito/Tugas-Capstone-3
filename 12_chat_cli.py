
import uuid

import config
from langfuse import get_client

from chat_service import ask, print_report

config.check_keys(["OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"])

history = []
session_id = "cli-" + uuid.uuid4().hex[:8]
print("tes chatbot. Satu sesi Langfuse =", session_id)
print("tes pertanyaan misalnya: 'Film apa yang punya rating tertinggi?'")
print("Ketik exit untuk quit.")
print()

while True:
    try:
        question = input("Kamu: ").strip()
    except EOFError:
        break
    if question == "":
        continue
    if question.lower() in ("exit", "quit", "keluar"):
        break

    result = ask(question, history, session_id=session_id, tags=["cli", "supervisor"])
    print()
    print_report(result)
    print()

    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": result["answer"]})

get_client().flush()
print("Sampai jumpa:", session_id)
