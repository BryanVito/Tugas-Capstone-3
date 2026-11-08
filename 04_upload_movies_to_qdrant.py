
import time
import config
from models import get_embeddings
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from movie_documents import load_movie_documents

BATCH_SIZE = 50        
PAUSE_SECONDS = 1.5    
MAX_TRIES = 3          
QDRANT_TIMEOUT = 120    

config.check_keys(["OPENAI_API_KEY", "QDRANT_URL", "QDRANT_API_KEY"])

#siapin data film yang mau di-upload ke Qdrant
collection_name = config.MOVIE_COLLECTION_NAME

documents, ids = load_movie_documents()

total_documents = len(documents)
print("Nama koleksi      :", collection_name)
print("Jumlah film       :", total_documents, "(satu film satu chunk, seharusnya 1000)")
print("Contoh isi satu film yang akan di-embedding:")
print(documents[0].page_content)
print("Metadata:", documents[0].metadata)

# sambung ke qdrant dan openai
client = QdrantClient(
    url=config.QDRANT_URL,
    api_key=config.QDRANT_API_KEY,
    prefer_grpc=True,
    timeout=QDRANT_TIMEOUT,
)

embeddings = get_embeddings()

#collection
if client.collection_exists(collection_name):
    print()
    print("Koleksi", collection_name, "UDAH ADA di Qdrant.")
    answer = input("Hapus koleksi lama lalu buat ulang? (y/n): ")
    if answer.lower() == "y":
        client.delete_collection(collection_name)
        print("Koleksi lama dihapus.")
    else:
        print("Cancelled. Tidak ada yang diubah.")
        raise SystemExit

client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=config.EMBEDDING_SIZE, distance=Distance.COSINE),
)
print("Koleksi baru dibuat (ukuran vektor", config.EMBEDDING_SIZE, ", jarak cosine).")

vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
)

#upload perbatch
print()
print("Mulai upload")
start_time = time.time()

for start in range(0, total_documents, BATCH_SIZE):
    end = start + BATCH_SIZE
    batch_documents = documents[start:end]
    batch_ids = ids[start:end]

    success = False
    for attempt in range(1, MAX_TRIES + 1):
        try:
            vector_store.add_documents(documents=batch_documents, ids=batch_ids)
            success = True
            break
        except Exception as error:
            print("Batch mulai dari", start, "error (percobaan", attempt, "):", error)
            time.sleep(5)

    if success is False:
        print("Batch mulai dari", start, "tetap gagal. Program berhenti.")
        print("Perbaiki masalahnya, lalu jalankan lagi (pilih y untuk hapus dan ulang).")
        raise SystemExit

    uploaded = min(end, total_documents)
    print("Terupload", uploaded, "dari", total_documents)
    time.sleep(PAUSE_SECONDS)

#cek hasil upload
seconds_used = round(time.time() - start_time)
count_result = client.count(collection_name=collection_name, exact=True)

print()
print("Selesai", seconds_used, "detik.")
print("Jumlah data di Qdrant :", count_result.count)
print("Jumlah yang diharapkan:", total_documents)
if count_result.count == total_documents:
    print("DONE. Vector database berhasil dibuat.")
else:
    print("Failed. Ada yang salah")
print("done")
