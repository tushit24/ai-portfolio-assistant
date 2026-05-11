"""
diagnose.py
-----------
Run this from your project root (same folder as main.py) to see
exactly what ChromaDB returns for the "projects" query and what
distances are coming back.

Usage:
    python diagnose.py
"""

import chromadb
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

print(f"ChromaDB path: {CHROMA_PATH}\n")

client = chromadb.PersistentClient(path=CHROMA_PATH)

queries_to_test = [
    ("projects",        "What projects has he built?"),
    ("projects",        "Tell me about his projects"),
    ("skills",          "What are his skills?"),
    ("experience",      "What is his work experience?"),
    ("certifications",  "What certifications does he have?"),
    ("resume_collection", "What projects has he built?"),  # general fallback
]

for collection_name, query in queries_to_test:
    col = client.get_or_create_collection(collection_name)
    count = col.count()
    print(f"{'='*60}")
    print(f"Collection : {collection_name} ({count} docs)")
    print(f"Query      : {query}")

    if count == 0:
        print("  ⚠ EMPTY — run ingest_resume.py first")
        continue

    results = col.query(
        query_texts=[query],
        n_results=min(4, count),
        include=["documents", "distances"]
    )

    docs  = results["documents"][0]
    dists = results["distances"][0]

    for i, (doc, dist) in enumerate(zip(docs, dists)):
        status = "✓ PASS (< 2.0)" if dist < 2.0 else "✗ FAIL (>= 2.0)"
        print(f"\n  Result #{i+1} | distance={dist:.4f} | {status}")
        print(f"  Preview: {doc[:120].strip()}...")

    print()

print("Done. Use the distances above to tune DISTANCE_THRESHOLD in main.py.")