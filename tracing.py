
from langfuse.langchain import CallbackHandler

DEFAULT_USER_ID = "capstone-user"


def make_run_config(session_id=None, user_id=DEFAULT_USER_ID, tags=None, run_name="capstone-chatbot"):
    """Membuat 'config' yang dikirim ke agent.invoke(...) supaya tercatat di Langfuse."""
    handler = CallbackHandler()

    metadata = {}
    if session_id:
        metadata["langfuse_session_id"] = session_id
    if user_id:
        metadata["langfuse_user_id"] = user_id
    if tags:
        metadata["langfuse_tags"] = list(tags)

    return {
        "callbacks": [handler],
        "metadata": metadata,
        "run_name": run_name,
        "recursion_limit": 60,
    }
