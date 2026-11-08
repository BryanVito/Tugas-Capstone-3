
from sql_tools import get_db, get_db_schema_tool, execute_query_tool

print("=" * 70)
print("test 1: skema database")
print("=" * 70)
schema_text = get_db_schema_tool.invoke({})
print(schema_text)

print("=" * 70)
print("test2: query yang benar")
print("=" * 70)
good_queries = [
    "SELECT title, imdb_rating FROM movies ORDER BY imdb_rating DESC LIMIT 5",
    "SELECT director, COUNT(*) AS total FROM movies GROUP BY director ORDER BY total DESC LIMIT 3",
    "SELECT m.title, m.released_year FROM movies m JOIN movie_genres g ON m.movie_id = g.movie_id "
    "WHERE g.genre = 'Sci-Fi' AND m.released_year >= 2010 ORDER BY m.imdb_rating DESC LIMIT 5",
    "SELECT ROUND(AVG(runtime_minutes), 1) AS average_runtime FROM movies WHERE genre LIKE '%Animation%'",
]
for query in good_queries:
    print("Query :", query)
    print("Hasil :", execute_query_tool.invoke({"query": query}))
    print()

print("=" * 70)
print("test 3: query yang salah")
print("=" * 70)
bad_query = "SELECT judul_film FROM movies LIMIT 3"   # kolom judul_film tidak ada
print("Query :", bad_query)
print("Hasil :", execute_query_tool.invoke({"query": bad_query}))
print()

print("=" * 70)
print("test 4: query berbahaya")
print("=" * 70)
dangerous_queries = [
    "DELETE FROM movies",
    "DROP TABLE movies",
    "UPDATE movies SET imdb_rating = 10",
    "SELECT 1; DROP TABLE movies",
]
for query in dangerous_queries:
    print("Query :", query)
    print("Hasil :", execute_query_tool.invoke({"query": query}))
    print()

print("=" * 70)
print("test 5: lapis pengaman 2, database read-only")
print("=" * 70)
print("Perintah : DELETE FROM movies")
print("Hasil    :", get_db().run_no_throw("DELETE FROM movies"))
print()
print("Jumlah film sekarang:", get_db().run("SELECT COUNT(*) FROM movies"), "(harus tetap 1000)")
