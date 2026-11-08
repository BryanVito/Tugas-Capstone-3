
import os
import sqlite3
import config
from imdb_data import load_clean_movies

#clean csv
movies_df, genres_df = load_clean_movies()

#new database file
if os.path.exists(config.IMDB_DB_PATH):
    os.remove(config.IMDB_DB_PATH)
    print("File database lama dihapus, akan dibuat ulang.")

connection = sqlite3.connect(config.IMDB_DB_PATH)

# Dua tabel dengan hubungan satu-ke-banyak (Session 16: primary key dan foreign key).
# Satu film punya banyak genre, jadi genre dipisah ke tabel sendiri.
create_tables_sql = """
CREATE TABLE movies (
    movie_id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    released_year INTEGER,
    certificate TEXT,
    runtime_minutes INTEGER,
    genre TEXT,
    imdb_rating REAL,
    overview TEXT,
    meta_score INTEGER,
    director TEXT,
    star1 TEXT,
    star2 TEXT,
    star3 TEXT,
    star4 TEXT,
    no_of_votes INTEGER,
    gross_usd INTEGER,
    poster_link TEXT
);

CREATE TABLE movie_genres (
    movie_id INTEGER NOT NULL,
    genre TEXT NOT NULL,
    PRIMARY KEY (movie_id, genre),
    FOREIGN KEY (movie_id) REFERENCES movies (movie_id)
);
"""
connection.executescript(create_tables_sql)
print("Dua tabel dibuat: movies dan movie_genres")

#isi tabel dengan data dari CSV
# if_exists="append" artinya: tabel udah ada,
movies_df.to_sql("movies", connection, if_exists="append", index=False)
genres_df.to_sql("movie_genres", connection, if_exists="append", index=False)
connection.commit()

#cek hasilnya
cursor = connection.cursor()
movie_count = cursor.execute("SELECT COUNT(*) FROM movies").fetchone()[0]
genre_count = cursor.execute("SELECT COUNT(*) FROM movie_genres").fetchone()[0]
print()
print("Jumlah film di tabel movies        :", movie_count, "(seharusnya 1000)")
print("Jumlah baris di tabel movie_genres :", genre_count)

print()
print("Cek beberapa pertanyaan sederhana langsung ke database:")
checks = [
    ("Film dengan rating tertinggi",
     "SELECT title, imdb_rating FROM movies ORDER BY imdb_rating DESC, no_of_votes DESC LIMIT 3"),
    ("Jumlah film per genre (5 teratas)",
     "SELECT genre, COUNT(*) AS total FROM movie_genres GROUP BY genre ORDER BY total DESC LIMIT 5"),
    ("Film yang tahunnya sudah diperbaiki (Apollo 13)",
     "SELECT title, released_year FROM movies WHERE title = 'Apollo 13'"),
    ("Film dengan pendapatan (Gross) kosong",
     "SELECT COUNT(*) FROM movies WHERE gross_usd IS NULL"),
    ("Film dengan pendapatan terbesar",
     "SELECT title, gross_usd FROM movies ORDER BY gross_usd DESC LIMIT 3"),
]
for label, sql in checks:
    print("-", label)
    for row in cursor.execute(sql).fetchall():
        print("    ", row)

connection.close()

print()
if movie_count == 1000:
    print("done. file database ada di:", config.IMDB_DB_PATH)
else:
    print("WARNING: jumlah film bukan 1000.")
