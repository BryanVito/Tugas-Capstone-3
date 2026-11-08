
import pandas as pd
import config


def load_clean_movies(verbose=True):
    """Membaca CSV IMDB lalu mengembalikan dua tabel pandas: (movies_df, genres_df)."""

    def say(text):
        if verbose:
            print(text)

    df = pd.read_csv(config.IMDB_CSV_PATH)
    say("Membaca CSV: " + str(len(df)) + " baris, " + str(len(df.columns)) + " kolom")

    # 1. Released_Year yang bukan angka
    bad_year_mask = ~df["Released_Year"].astype(str).str.fullmatch(r"\d{4}")
    bad_year_count = int(bad_year_mask.sum())
    # Satu-satunya yang salah adalah Apollo 13 (tertulis "PG"). Filmnya rilis tahun 1995.
    apollo_mask = (df["Series_Title"] == "Apollo 13") & (df["Released_Year"] == "PG")
    df.loc[apollo_mask, "Released_Year"] = "1995"
    still_bad = int((~df["Released_Year"].astype(str).str.fullmatch(r"\d{4}")).sum())
    say("Released_Year bukan angka: " + str(bad_year_count) + " baris -> setelah diperbaiki sisa " + str(still_bad))
    df["Released_Year"] = df["Released_Year"].astype(int)

    # 2. Runtime: "142 min"
    df["Runtime"] = df["Runtime"].str.extract(r"(\d+)")[0].astype(int)
    say("Runtime diubah dari teks '142 min' jadi angka menit")

    # 3. Gross: "28,341,469"
    gross_text = df["Gross"].str.replace(",", "", regex=False)
    df["Gross"] = pd.to_numeric(gross_text, errors="coerce").astype("Int64")
    say("Gross diubah dari teks berkoma jadi angka. Kosong dibiarkan kosong: " + str(int(df["Gross"].isna().sum())) + " film")

    # 4. Meta_score jadi bilangan bulat
    df["Meta_score"] = df["Meta_score"].astype("Int64")
    say("Meta_score kosong dibiarkan kosong: " + str(int(df["Meta_score"].isna().sum())) + " film")
    say("Certificate kosong dibiarkan kosong: " + str(int(df["Certificate"].isna().sum())) + " film")

    # 5. Beri nomor film (movie_id) dan samakan nama kolom
    df.insert(0, "movie_id", range(1, len(df) + 1))
    df = df.rename(columns={
        "Series_Title": "title",
        "Released_Year": "released_year",
        "Certificate": "certificate",
        "Runtime": "runtime_minutes",
        "Genre": "genre",
        "IMDB_Rating": "imdb_rating",
        "Overview": "overview",
        "Meta_score": "meta_score",
        "Director": "director",
        "Star1": "star1",
        "Star2": "star2",
        "Star3": "star3",
        "Star4": "star4",
        "No_of_Votes": "no_of_votes",
        "Gross": "gross_usd",
        "Poster_Link": "poster_link",
    })

    # Urutan kolom di tabel movies
    movie_columns = [
        "movie_id", "title", "released_year", "certificate", "runtime_minutes", "genre",
        "imdb_rating", "overview", "meta_score", "director", "star1", "star2", "star3", "star4",
        "no_of_votes", "gross_usd", "poster_link",
    ]
    movies_df = df[movie_columns].copy()

    # 6. Tabel kedua: satu baris per film per genre
    genre_rows = []
    for _, row in movies_df.iterrows():
        for one_genre in str(row["genre"]).split(","):
            one_genre = one_genre.strip()
            if one_genre != "":
                genre_rows.append({"movie_id": int(row["movie_id"]), "genre": one_genre})
    genres_df = pd.DataFrame(genre_rows)
    say("Tabel movie_genres: " + str(len(genres_df)) + " baris (satu baris per film per genre)")

    return movies_df, genres_df
