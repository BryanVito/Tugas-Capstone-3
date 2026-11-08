
import uuid

import config
from langchain_core.messages import HumanMessage
from langfuse import get_client

from chat_service import analyze_messages, print_report
from film_search_agent import build_film_search_agent
from tracing import make_run_config

config.check_keys(["OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"])

agent = build_film_search_agent()
session_id = "test-film-search-" + uuid.uuid4().hex[:8]

questions = [
    "Recommend a movie about a thief who enters people's dreams.",
    "Which movies are about toys that come to life?",
    "Cari film tentang keluarga mafia di Amerika.",             
    "Movies similar to The Lion King",
    "How to bake a chocolate cake?",                            
]

for question in questions:
    print("=" * 70)
    print("Pertanyaan:", question)
    print("=" * 70)
    run_config = make_run_config(session_id=session_id, tags=["test", "film-search-agent"], run_name="test-film-search-agent")
    result = agent.invoke({"messages": [HumanMessage(content=question)]}, config=run_config)
    report = analyze_messages(result["messages"][1:])
    print_report(report)
    print()

get_client().flush()
print("Selesai.")
