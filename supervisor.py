
import config
from langgraph_supervisor import create_supervisor

from film_agent import build_film_agent
from film_search_agent import build_film_search_agent
from models import get_llm
from prompts import load_prompt


def build_supervisor():
    film_stats_agent = build_film_agent()
    film_search_agent = build_film_search_agent()

    supervisor_prompt = load_prompt(config.PROMPT_SUPERVISOR)

    workflow = create_supervisor(
        agents=[film_search_agent, film_stats_agent],
        model=get_llm(config.SUPERVISOR_LLM_MODEL),
        prompt=supervisor_prompt,
        output_mode="full_history",
    )
    return workflow.compile()
