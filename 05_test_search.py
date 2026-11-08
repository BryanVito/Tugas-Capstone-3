
import config
from models import get_embeddings
from langchain_qdrant import QdrantVectorStore

COLLECTION_TO_TEST = config.MOVIE_COLLECTION_NAME
print("tes collection:", COLLECTION_TO_TEST)

config.check_keys(["OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"])

embeddings = get_embeddings()

vector_store = QdrantVectorStore.from_existing_collection(
    embedding=embeddings,
    collection_name=COLLECTION_TO_TEST,
    url=config.QDRANT_URL,
    api_key=config.QDRANT_API_KEY,
)

relevant_questions = [
    "a thief who steals secrets by entering people's dreams",
    "toys that come to life when humans are not around",
    "a young boxer from a poor neighborhood fights for the championship",
    "prisoners trying to escape from a World War II camp",
    "a lonely robot cleaning up garbage on an abandoned Earth",
    "cari film tentang keluarga mafia di Amerika",   #pake indo tes
]

irrelevant_questions = [
    "how to bake a chocolate cake",
    "python programming tutorial for beginners",
    "what is the weather forecast for tomorrow",
]


def run_questions(question_list, label):
    print("=" * 70)
    print(label)
    print("=" * 70)
    top_scores = []
    for question in question_list:
        results = vector_store.similarity_search_with_score(question, k=3)
        print("Pertanyaan:", question)
        for document, score in results:
            title = document.metadata["title"]
            year = document.metadata["released_year"]
            rating = document.metadata["imdb_rating"]
            print("   skor", round(score, 3), "|", title, "(" + str(year) + ")", "| rating", rating)
        if len(results) > 0:
            top_scores.append(results[0][1])
        print()
    return top_scores


relevant_top_scores = run_questions(relevant_questions, "PERTANYAAN YANG SEHARUSNYA KETEMU")
irrelevant_top_scores = run_questions(irrelevant_questions, "PERTANYAAN YANG SEHARUSNYA TIDAK KETEMU")

print("=" * 70)
print("summary buat milih threshold")
print("=" * 70)
print("Skor teratas terendah dari pertanyaan relevan   :", round(min(relevant_top_scores), 3))
print("Skor teratas tertinggi dari pertanyaan tidak relevan:", round(max(irrelevant_top_scores), 3))
print("SCORE_THRESHOLD saat ini di config.py            :", config.SCORE_THRESHOLD)
print()
print("Cara memilih: threshold sebaiknya DI ANTARA dua angka di atas.")
print("Kalau dua angka itu saling tumpang tindih, pilih angka yang sedikit di atas")
print("skor tertinggi pertanyaan tidak relevan, lalu tes lagi dengan pertanyaan lain.")
