from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import os

from groq import Groq
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================

load_dotenv()

# =========================
# GROQ CLIENT
# =========================

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# =========================
# FASTAPI APP
# =========================

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# CHROMA DB
# =========================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

chroma_client = chromadb.PersistentClient(path=CHROMA_PATH)

COLLECTIONS = {
    "projects": chroma_client.get_or_create_collection("projects"),
    "certifications": chroma_client.get_or_create_collection("certifications"),
    "experience": chroma_client.get_or_create_collection("experience"),
    "skills": chroma_client.get_or_create_collection("skills"),
    "general": chroma_client.get_or_create_collection("resume_collection"),
}

# =========================
# QUERY ROUTER
# =========================

def route_query(query: str) -> str:
    q = query.lower()

    project_keywords = [
        "sheets",
"firebase",
"realtime",
"full stack","project", "built", "made", "created", "app",
        "application", "website", "build", "developed",
        "spendy", "collab", "churn", "flutter",
        "nextjs", "next.js", "streamlit" , "app development"
    ]

    cert_keywords = [
        "certif", "course", "nptel", "google",
        "oracle", "credential", "award",
        "recommendation"
    ]

    exp_keywords = [
        "experience", "intern", "work", "job",
        "company", "role", "position",
        "e-summit", "geostrata", "ecell", "e-cell"
    ]

    skill_keywords = [
        "skill", "language", "tech", "stack",
        "framework", "technology", "technologies",
        "tool", "proficient"
    ]

    if any(k in q for k in project_keywords):
        return "projects"

    if any(k in q for k in cert_keywords):
        return "certifications"

    if any(k in q for k in exp_keywords):
        return "experience"

    if any(k in q for k in skill_keywords):
        return "skills"

    return "general"

# =========================
# SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """
You are Tushit Tiwari's premium AI Portfolio Assistant.

You help recruiters and visitors understand:
- projects
- technical skills
- certifications
- experience
- technical strengths
- career interests
- job suitability

IMPORTANT RULES:

- ONLY answer using portfolio context
- NEVER invent technologies, projects, companies, or experience
- NEVER merge projects together
- NEVER repeat information
- NEVER behave like a generic chatbot
- NEVER ask unnecessary follow-up questions
- NEVER generate HTML or code snippets

Tushit is:
- a third-year B.Tech student
- studying Computer Science & Engineering
- specializing in E-Commerce Technology
- at VIT Bhopal University

Present him professionally as:
- a strong aspiring software engineer
- AI-focused full stack developer
- technically skilled engineering student

RESPONSE STYLE:
- concise
- recruiter-friendly
- markdown formatted
- use headings and bullet points
- avoid giant paragraphs

FOR PROJECT QUESTIONS:

## Project Name
- Description
- Tech Stack
- Key Features

FOR JOB SUITABILITY QUESTIONS:

## Why Tushit is a Strong Fit
- strengths
- matching skills
- technical alignment

## Relevant Projects
- project name: relevance

## Overall Assessment
- concise conclusion

If information is unavailable say:
"That information is not available in Tushit's portfolio."
"""

# =========================
# REQUEST MODEL
# =========================

class ChatRequest(BaseModel):
    query: str

# =========================
# ROOT
# =========================

@app.get("/")
def root():
    return {
        "message": "Tushit AI Portfolio Assistant API Running"
    }

# =========================
# DEBUG
# =========================

@app.get("/debug")
def debug():
    info = {}

    for key, col in COLLECTIONS.items():
        try:
            info[key] = col.count()
        except Exception as e:
            info[key] = f"error: {str(e)}"

    return {
        "chroma_path": CHROMA_PATH,
        "collections": info
    }

# =========================
# CHAT ENDPOINT
# =========================

@app.post("/chat")
async def chat(request: ChatRequest):

    query = request.query.strip()

    # =========================
    # ROUTE QUERY
    # =========================

    collection_key = route_query(query)
    collection = COLLECTIONS[collection_key]

    # =========================
    # QUERY CHROMA
    # =========================

    DISTANCE_THRESHOLD = 1.8
    N_RESULTS = 6

    def fetch_docs(col, n=N_RESULTS):

        try:
            count = col.count()

            if count == 0:
                return [], []

            actual_n = min(n, count)

            results = col.query(
                query_texts=[query],
                n_results=actual_n,
                include=["documents", "distances"]
            )

            docs = results.get("documents", [[]])[0]
            dists = results.get("distances", [[]])[0]

            return docs, dists

        except Exception:
            return [], []

    docs, dists = fetch_docs(collection)

    # =========================
    # FILTER RESULTS
    # =========================

    filtered = [
        doc for doc, dist in zip(docs, dists)
        if dist < DISTANCE_THRESHOLD
    ]

    # =========================
    # FALLBACK TO GENERAL
    # =========================

    if not filtered and collection_key != "general":

        fallback_docs, fallback_dists = fetch_docs(
            COLLECTIONS["general"],
            n=5
        )

        filtered = [
            doc for doc, dist in zip(fallback_docs, fallback_dists)
            if dist < DISTANCE_THRESHOLD
        ]

    # =========================
    # LAST RESORT
    # =========================

    if not filtered:
        all_docs, _ = fetch_docs(collection, n=N_RESULTS)
        filtered = all_docs

    # =========================
    # DEDUPLICATION
    # =========================

    unique_docs = []

    for doc in filtered:

        cleaned = doc.strip()

        if cleaned and cleaned not in unique_docs:
            unique_docs.append(cleaned)

    # =========================
    # NO CONTEXT FOUND
    # =========================

    if not unique_docs:
        return {
            "response": (
                "That information is not available in "
                "Tushit's portfolio."
            )
        }

    context = "\n\n".join(unique_docs)

    # =========================
    # FINAL PROMPT
    # =========================

    final_prompt = f"""
PORTFOLIO CONTEXT:
{context}

QUESTION:
{query}

STRICT INSTRUCTIONS:

- Answer ONLY from the portfolio context
- No hallucinations
- No fake technologies
- No fake projects
- No HTML
- No code snippets
- Keep response concise
- Keep response recruiter-friendly
- Use markdown formatting
- Use bullet points
- Avoid repetition
- Complete the response fully
- Do not stop mid-sentence

ONLY return the final answer.
"""

    # =========================
    # GROQ RESPONSE
    # =========================

    response = groq_client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {
                "role": "system",
                "content": SYSTEM_PROMPT,
            },
            {
                "role": "user",
                "content": final_prompt,
            }
        ],
        temperature=0,
        max_tokens=500,
    )

    answer = response.choices[0].message.content

    # =========================
    # RETURN
    # =========================

    return {
        "response": answer
    }