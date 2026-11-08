
import uuid

from langchain_core.documents import Document

from imdb_data import load_clean_movies


def build_movie_text(row):
    """Menyusun teks yang akan diubah jadi vektor (dan dicari) untuk satu film.
    Judul, tahun, genre, sutradara, dan pemeran ikut ditulis, supaya pencarian seperti
    'film Christopher Nolan tentang mimpi' juga bisa menemukan filmnya.
    Rating TIDAK dimasukkan ke teks: angka rating tidak membantu pencarian makna.
    Rating disimpan di metadata, lalu ditampilkan di hasil pencarian."""
    stars = []
    for column in ["star1", "star2", "star3", "star4"]:
        if str(row[column]) != "" and str(row[column]) != "nan":
            stars.append(str(row[column]))

    lines = [
        "Title: " + str(row["title"]) + " (" + str(int(row["released_year"])) + ")",
        "Genre: " + str(row["genre"]),
        "Director: " + str(row["director"]),
        "Stars: " + ", ".join(stars),
        "Overview: " + str(row["overview"]),
    ]
    return "\n".join(lines)


def load_movie_documents():
    """Mengembalikan dua list: documents (satu per film) dan ids (nomor unik tiap film)."""
    movies_df, _ = load_clean_movies(verbose=False)

    documents = []
    ids = []

    for _, row in movies_df.iterrows():
        movie_id = int(row["movie_id"])

        page_content = build_movie_text(row)

        metadata = {
            "movie_id": movie_id,
            "title": str(row["title"]),
            "released_year": int(row["released_year"]),
            "genre": str(row["genre"]),
            "director": str(row["director"]),
            "imdb_rating": float(row["imdb_rating"]),
            "runtime_minutes": int(row["runtime_minutes"]),
            "source": "imdb_top_1000.csv",
        }

        documents.append(Document(page_content=page_content, metadata=metadata))

        ids.append(str(uuid.uuid5(uuid.NAMESPACE_DNS, "imdb-movie-" + str(movie_id))))

    return documents, ids
