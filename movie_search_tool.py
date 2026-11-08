
import config
from langchain_core.tools import tool
from models import get_embeddings
from langchain_qdrant import QdrantVectorStore

_vector_store = None 


def get_vector_store():
    """Membuka koleksi Qdrant yang sudah ada. Hanya dilakukan sekali, lalu dipakai ulang."""
    global _vector_store
    if _vector_store is None:
        config.check_keys(["OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"])
        _vector_store = QdrantVectorStore.from_existing_collection(
            embedding=get_embeddings(),
            collection_name=config.MOVIE_COLLECTION_NAME,
            url=config.QDRANT_URL,
            api_key=config.QDRANT_API_KEY,
            timeout=60, 
        )
    return _vector_store


@tool
def search_movies(question: str) -> str:
    """Search the IMDB Top 1000 movie database by meaning (semantic search).

    Use this tool when the user describes a plot, story, theme, mood, setting, or character,
    or asks for movies similar to another movie or movies about a topic
    (for example "a movie about dreams inside dreams" or "movies like Toy Story").
    The input must be a short search sentence in English that describes the movie to look for.
    Each result has the title, year, genre, director, stars, IMDB rating, and a short plot overview.
    """
    results = get_vector_store().similarity_search_with_score(question, k=config.TOP_K)
    good_results = []
    for document, score in results:
        if score >= config.SCORE_THRESHOLD:
            good_results.append((document, score))
    if len(good_results) == 0:
        return "No relevant movie found in the database for this question."
    output_text = ""
    number = 1
    for document, score in good_results:
        meta = document.metadata
        output_text = output_text + "Result " + str(number) + "\n"
        output_text = output_text + "Title: " + str(meta["title"]) + " (" + str(meta["released_year"]) + ")\n"
        output_text = output_text + "Genre: " + str(meta["genre"]) + "\n"
        output_text = output_text + "Director: " + str(meta["director"]) + "\n"
        output_text = output_text + "IMDB rating: " + str(meta["imdb_rating"]) + "\n"
        output_text = output_text + "Runtime: " + str(meta["runtime_minutes"]) + " min\n"
        output_text = output_text + "Similarity score: " + str(round(score, 3)) + "\n"
        output_text = output_text + "Content:\n" + document.page_content + "\n\n"
        number = number + 1
    output_text = output_text + (
        "NEXT STEP: answer using ONLY the movies listed above. "
        "Keep every title, year, and rating exactly as shown. Do not add movies from your own knowledge."
    )
    return output_text

if __name__ == "__main__":
    test_questions = [
        "a thief who steals secrets by entering people's dreams",
        "toys that come to life when humans are not around",
        "how to bake a chocolate cake",
    ]
    for test_question in test_questions:
        print("=" * 70)
        print("Pertanyaan:", test_question)
        print("=" * 70)
        result_text = search_movies.invoke({"question": test_question})
        print(result_text)
