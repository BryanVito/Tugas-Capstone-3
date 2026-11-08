
import config
from langgraph.prebuilt import create_react_agent

from models import get_llm
from prompts import load_prompt
from sql_tools import SQL_TOOLS, get_db


def build_film_agent():
    system_prompt = load_prompt(
        config.PROMPT_FILM_AGENT,
        dialect=get_db().dialect,     
        top_k=str(config.SQL_TOP_K),
    )
    return create_react_agent(
        model=get_llm(config.AGENT_LLM_MODEL),
        tools=SQL_TOOLS,
        prompt=system_prompt,
        name="film_stats_expert",
    )
