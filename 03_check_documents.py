
from movie_documents import load_movie_documents

documents, ids = load_movie_documents()

total_movies = len(documents)

total_characters = 0
longest_text = 0
for document in documents:
    text_length = len(document.page_content)
    total_characters = total_characters + text_length
    if text_length > longest_text:
        longest_text = text_length

print("Jumlah film (= jumlah chunk):", total_movies, "(satu film satu chunk)")
print("Rata-rata huruf per chunk:", round(total_characters / total_movies))
print("Chunk terpanjang (huruf):", longest_text)


estimated_tokens = total_characters / 4
estimated_cost_dollar = estimated_tokens / 1_000_000 * 0.02
print()
print("Perkiraan jumlah token     :", round(estimated_tokens))
print("Perkiraan biaya embedding    : sekitar", round(estimated_cost_dollar, 4), "dolar")

print()
print("=" * 60)
print("contoh 3 film pertama")
print("=" * 60)
for i in range(3):
    print("--- Film ke-", i + 1, "---")
    print("ID       :", ids[i])
    print("Metadata :", documents[i].metadata)
    print("Isi (inilah teks yang diubah jadi vektor):")
    print(documents[i].page_content)
    print()
