
import time
import uuid
import random
from urllib.parse import urlparse

import config
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams, PointStruct

config.check_keys(["QDRANT_URL", "QDRANT_API_KEY"])

COLLECTION = "diag_test"
TIMEOUT = 30  

print("Server Qdrant:", urlparse(config.QDRANT_URL).netloc)
print()


def make_points(how_many):
    points = []
    for _ in range(how_many):
        vector = [random.random() for _ in range(config.EMBEDDING_SIZE)]
        points.append(PointStruct(id=str(uuid.uuid4()), vector=vector, payload={"note": "diag"}))
    return points


def try_upload(client, label, how_many):
    points = make_points(how_many)
    start = time.time()
    try:
        client.upsert(collection_name=COLLECTION, points=points, wait=True)
        seconds = round(time.time() - start, 1)
        print("  ", label, "| kirim", how_many, "titik: BERHASIL dalam", seconds, "detik")
        return True
    except Exception as error:
        seconds = round(time.time() - start, 1)
        print("  ", label, "| kirim", how_many, "titik: GAGAL setelah", seconds, "detik ->", error)
        return False


# Cara 1
print("=== Cara 1: REST ===")
rest_client = QdrantClient(url=config.QDRANT_URL, api_key=config.QDRANT_API_KEY, timeout=TIMEOUT)

if rest_client.collection_exists(COLLECTION):
    rest_client.delete_collection(COLLECTION)
rest_client.create_collection(
    collection_name=COLLECTION,
    vectors_config=VectorParams(size=config.EMBEDDING_SIZE, distance=Distance.COSINE),
)

rest_ok = True
for how_many in [1, 5, 20, 50]:
    ok = try_upload(rest_client, "REST", how_many)
    if not ok:
        rest_ok = False
        break

# Cara 2
print()
print("=== Cara 2: gRPC ===")
try:
    grpc_client = QdrantClient(
        url=config.QDRANT_URL,
        api_key=config.QDRANT_API_KEY,
        prefer_grpc=True,
        timeout=TIMEOUT,
    )
    for how_many in [1, 20, 50]:
        ok = try_upload(grpc_client, "gRPC", how_many)
        if not ok:
            break
except Exception as error:
    print("   gRPC tidak bisa dipakai:", error)


print()
try:
    rest_client.delete_collection(COLLECTION)
    print("Koleksi percobaan", COLLECTION, "udah dihapus.")
except Exception as error:
    print("Gagal menghapus koleksi percobaan:", error)

print()
print("Selesai.")
