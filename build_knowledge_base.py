import chromadb
import uuid
import io

from pypdf import PdfReader

from chromadb.utils.embedding_functions.ollama_embedding_function import (
    OllamaEmbeddingFunction,
)

# =========================================
# CHROMADB CLIENT
# =========================================

client = chromadb.PersistentClient(path="./chroma_db")

# =========================================
# EMBEDDING FUNCTION
# =========================================

ef = OllamaEmbeddingFunction(
    model_name="nomic-embed-text",
    url="http://localhost:11434",
)

# =========================================
# RESUME COLLECTION
# =========================================

resume_collection = client.get_or_create_collection(
    name="resume_collection",
    embedding_function=ef,
)

# =========================================
# CLEAR OLD DATA
# =========================================

try:
    existing = resume_collection.get()

    if existing["ids"]:
        resume_collection.delete(
            ids=existing["ids"]
        )

        print("Old resume collection cleared.")

except Exception as e:
    print("No old data found.")

# =========================================
# LOAD PROFILE.TXT
# =========================================

with open(
    "profile.txt",
    "r",
    encoding="utf-8"
) as f:

    profile_text = f.read()

# =========================================
# LOAD RESUME PDF
# =========================================

resume_pdf_path = "Tushit_Tiwari_Resume.pdf"

resume_text = ""

try:

    with open(resume_pdf_path, "rb") as pdf_file:

        pdf = PdfReader(pdf_file)

        for page in pdf.pages:

            extracted = page.extract_text()

            if extracted:
                resume_text += extracted + "\n"

    print("Resume PDF loaded successfully.")

except Exception as e:

    print("Resume PDF not found or failed to load.")
    print(e)

# =========================================
# COMBINE TEXT
# =========================================

combined_text = profile_text + "\n\n" + resume_text

# =========================================
# SMART CHUNKING
# =========================================

def split_text(text, chunk_size=700):

    text = text.replace("\n", " ")

    sentences = text.split(". ")

    chunks = []

    current_chunk = ""

    for sentence in sentences:

        if len(current_chunk) + len(sentence) < chunk_size:

            current_chunk += sentence + ". "

        else:

            chunks.append(
                current_chunk.strip()
            )

            current_chunk = sentence + ". "

    if current_chunk:

        chunks.append(
            current_chunk.strip()
        )

    return chunks

chunks = split_text(combined_text)

print(f"Created {len(chunks)} chunks.")

# =========================================
# IDS
# =========================================

ids = [
    str(uuid.uuid4())
    for _ in chunks
]

# =========================================
# METADATA
# =========================================

metadatas = []

for i in range(len(chunks)):

    metadatas.append(
        {
            "source": "portfolio_knowledge_base",
            "chunk_index": i,
        }
    )

# =========================================
# STORE EMBEDDINGS
# =========================================

resume_collection.add(
    ids=ids,
    documents=chunks,
    metadatas=metadatas,
)

print(
    f"Added {len(chunks)} chunks to resume_collection."
)

print("Knowledge base built successfully!")