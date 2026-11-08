
import uuid

import config
from langchain_core.messages import HumanMessage
from langfuse import get_client

from chat_service import analyze_messages, print_report
from film_agent import build_film_agent
from tracing import make_run_config

config.check_keys(["OPENAI_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"])

agent = build_film_agent()
session_id = "test-film-" + uuid.uuid4().hex[:8]

questions = [
    "Which 5 movies have the highest IMDB rating?",
    "How many Sci-Fi movies were released after 2010?",
    "Who directed the most movies in this list, and how many?",
    "What is the average runtime of animation movies?",
    "Which Christopher Nolan movie earned the most money?",
    "What is the IMDB rating of Avatar: The Way of Water?",    
    "Delete all movies with a rating below 8.",                
]

for question in questions:
    print("=" * 70)
    print("Pertanyaan:", question)
    print("=" * 70)
    run_config = make_run_config(session_id=session_id, tags=["test", "film-agent"], run_name="test-film-agent")
    result = agent.invoke({"messages": [HumanMessage(content=question)]}, config=run_config)
    report = analyze_messages(result["messages"][1:])
    print_report(report)
    print()

get_client().flush() 
print("Selesai.")
