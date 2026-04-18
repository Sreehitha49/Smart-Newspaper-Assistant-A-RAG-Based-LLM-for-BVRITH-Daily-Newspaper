import chromadb
from sentence_transformers import SentenceTransformer
from config import CHROMA_DIR, COLLECTION, PDF_FOLDER
from helpers import load_all_files

# Load embedding model
print("Loading embedding model…")
embedder = SentenceTransformer("all-MiniLM-L6-v2")
print("Embedder ready ✓")

# Initialize ChromaDB
client = chromadb.PersistentClient(path=CHROMA_DIR)

try:
    col = client.get_collection(COLLECTION)
    print(f"Loaded existing collection: {col.count()} chunks ✓")
except Exception:
    col = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})
    print("Created new collection ✓")


def build_database():
    """Build the vector database from scratch (clears existing data)"""
    global col
    try:
        client.delete_collection(COLLECTION)
    except Exception:
        pass
    col = client.create_collection(COLLECTION, metadata={"hnsw:space": "cosine"})

    docs, ids, meta = load_all_files(PDF_FOLDER)

    print("\nGenerating embeddings and storing…")
    BATCH = 50
    for i in range(0, len(docs), BATCH):
        emb = embedder.encode(docs[i:i + BATCH]).tolist()
        col.add(
            documents=docs[i:i + BATCH],
            embeddings=emb,
            ids=ids[i:i + BATCH],
            metadatas=meta[i:i + BATCH]
        )
        print(f"  {min(i + BATCH, len(docs))}/{len(docs)} stored")

    print(f"\nDatabase ready ✓ ({col.count()} total chunks)")


def get_collection():
    return col


def get_embedder():
    return embedder