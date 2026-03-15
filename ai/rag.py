import os
import faiss
import pickle
import numpy as np
from sentence_transformers import SentenceTransformer
from ai.ingest import extract_text, chunk_text

UPLOAD_DIR = "knowledge/uploads"
INDEX_DIR = "knowledge/vector_index"

INDEX_FILE = os.path.join(INDEX_DIR, "faiss.index")
CHUNK_FILE = os.path.join(INDEX_DIR, "chunks.pkl")

model = SentenceTransformer("all-MiniLM-L6-v2")

index = None
chunks = []


def build_index():

    global index, chunks

    print("Building knowledge index...")

    texts = []

    for file in os.listdir(UPLOAD_DIR):

        path = os.path.join(UPLOAD_DIR, file)

        print("Processing:", file)

        text = extract_text(path)

        if not text.strip():
            continue

        texts.extend(chunk_text(text))

    embeddings = model.encode(texts)

    dim = embeddings.shape[1]

    index = faiss.IndexFlatL2(dim)

    index.add(np.array(embeddings))

    chunks = texts

    faiss.write_index(index, INDEX_FILE)

    with open(CHUNK_FILE, "wb") as f:
        pickle.dump(chunks, f)

    print("Index built successfully")


def load_index():

    global index, chunks

    if not os.path.exists(INDEX_FILE):
        print("No index found. Build it first.")
        return

    index = faiss.read_index(INDEX_FILE)

    with open(CHUNK_FILE, "rb") as f:
        chunks = pickle.load(f)

    print("Knowledge index loaded")

def search(query, k=3):

    if index is None:
        return []

    query_vector = model.encode([query])

    distances, ids = index.search(np.array(query_vector), k)

    results = []

    print("\n===== RAG RETRIEVAL =====")
    print("Query:", query)

    for i in ids[0]:
        if i < len(chunks):
            chunk = chunks[i]
            print("\nRetrieved chunk:\n", chunk[:200])
            results.append(chunk)

    return results