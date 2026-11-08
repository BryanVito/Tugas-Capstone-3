
import uuid

import config
from langfuse import get_client

from chat_service import ask, print_report

config.check_keys(["OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY", "LANGFUSE_PUBLIC_KEY", "LANGFUSE_SECRET_KEY"])

questions = [
    "Hi! What can you help me with?",
    "Which movie has the highest IMDB rating?",                 
    "Who directed it?",                                          
    "Recommend a movie about a thief who enters people's dreams.",  
    "Who directed that movie, and what other movies did he make in this list?",   
    "What are the highest rated movies about space or time travel?",  
    "What is the capital of France?",                            
]

history = []                                  
session_id = "test-supervisor-" + uuid.uuid4().hex[:8]

for question in questions:
    print("=" * 70)
    print("User:", question)
    print("(history yang dikirim:", min(len(history), config.CHAT_HISTORY_TURNS * 2), "dari pertanyaan sebelumnya)")
    print("=" * 70)

    result = ask(question, history, session_id=session_id, tags=["test", "supervisor"])
    print_report(result)
    print()

    history.append({"role": "user", "content": question})
    history.append({"role": "assistant", "content": result["answer"]})

get_client().flush()
print("Selesai.:", session_id)
