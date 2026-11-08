
import config
from langgraph.prebuilt import create_react_agent

from models import get_llm
from movie_search_tool import search_movies
from prompts import load_prompt


def build_film_search_agent():
    system_prompt = load_prompt(config.PROMPT_FILM_SEARCH_AGENT)
    return create_react_agent(
        model=get_llm(config.AGENT_LLM_MODEL),
        tools=[search_movies],
        prompt=system_prompt,
        name="film_search_expert",
    )
