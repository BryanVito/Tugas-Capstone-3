
import pandas as pd
import config

print("=" * 60)
print("IMDB TOP 1000 (dipakai untuk RAG ke Qdrant dan untuk agent SQL)")
print("=" * 60)

imdb_df = pd.read_csv(config.IMDB_CSV_PATH)

print("Jumlah baris (jumlah film):", len(imdb_df))
print("Nama kolom:", list(imdb_df.columns))
print()

print("Jumlah data kosong per kolom (hanya yang ada kosongnya):")
missing_count = imdb_df.isna().sum()
print(missing_count[missing_count > 0])
print()

print("3 baris pertama (tanpa kolom Poster_Link supaya muat di layar):")
print(imdb_df.drop(columns=["Poster_Link"]).head(3).to_string())
print()


imdb_df["overview_length"] = imdb_df["Overview"].str.len()
print("Jumlah huruf:")
print(imdb_df["overview_length"].describe())
print()
print("Contoh Overview di film pertama:")
print(imdb_df["Overview"].iloc[0])
print()


print("Contoh isi kolom Gross (teks dengan koma):", imdb_df["Gross"].dropna().head(3).tolist())
print("Contoh isi kolom Runtime :", imdb_df["Runtime"].head(3).tolist())


not_number_mask = pd.to_numeric(imdb_df["Released_Year"], errors="coerce").isna()
print("Baris Released_Year yang bukan angka:")
print(imdb_df[not_number_mask][["Series_Title", "Released_Year"]])
