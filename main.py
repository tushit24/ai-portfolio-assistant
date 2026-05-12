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

def route_query(query: str):

    q = query.lower()

    summary_keywords = [
        "summary",
        "summarize",
        "overview",
        "about",
        "profile",
        "who is",
        "tell me about",
        "introduce",
    ]

    project_keywords = [
        "sheets",
        "firebase",
        "realtime",
        "full stack",
        "project",
        "built",
        "made",
        "created",
        "app",
        "application",
        "website",
        "build",
        "developed",
        "spendy",
        "collab",
        "churn",
        "flutter",
        "nextjs",
        "next.js",
        "streamlit",
        "app development",
    ]

    cert_keywords = [
        "certif",
        "course",
        "nptel",
        "google",
        "oracle",
        "credential",
        "award",
        "recommendation",
    ]

    exp_keywords = [
        "experience",
        "intern",
        "work",
        "job",
        "company",
        "role",
        "position",
        "e-summit",
        "geostrata",
        "ecell",
        "e-cell",
    ]

    skill_keywords = [
        "skill",
        "language",
        "tech",
        "stack",
        "framework",
        "technology",
        "technologies",
        "tool",
        "proficient",
    ]

    if any(k in q for k in summary_keywords):
        return ["general", "projects", "experience", "skills"]

    if any(k in q for k in project_keywords):
        return ["projects"]

    if any(k in q for k in cert_keywords):
        return ["certifications"]

    if any(k in q for k in exp_keywords):
        return ["experience", "projects"]

    if any(k in q for k in skill_keywords):
        return ["skills", "projects"]

    return ["general"]

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

    collection_keys = route_query(query)

    # =========================
    # QUERY CHROMA
    # =========================

    DISTANCE_THRESHOLD = 1.8
    N_RESULTS = 10

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

    # =========================
    # MULTI COLLECTION RETRIEVAL
    # =========================

    all_filtered_docs = []

    for key in collection_keys:

        collection = COLLECTIONS[key]

        docs, dists = fetch_docs(collection)

        filtered = [
            doc for doc, dist in zip(docs, dists)
            if dist < DISTANCE_THRESHOLD
        ]

        # fallback to general
        if not filtered:
            fallback_docs, fallback_dists = fetch_docs(
                COLLECTIONS["general"],
                n=6
            )

            filtered = [
                doc for doc, dist in zip(fallback_docs, fallback_dists)
                if dist < DISTANCE_THRESHOLD
            ]

        # last resort
        if not filtered:
            all_docs, _ = fetch_docs(collection, n=N_RESULTS)
            filtered = all_docs

        all_filtered_docs.extend(filtered)

    filtered = all_filtered_docs

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

    # =========================
    # CONTEXT
    # =========================

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

- Answer ONLY using the portfolio context
- NEVER hallucinate
- NEVER invent projects, roles, technologies, or companies
- NEVER merge projects together
- NEVER generate HTML or code snippets
- Keep responses recruiter-friendly
- Use markdown formatting
- Use headings and bullet points
- Avoid repetition
- Complete the response fully
- Do not stop mid-sentence

IMPORTANT PRIORITY RULES:

- When summarizing Tushit's profile or projects, ALWAYS mention:
  1. Spendy
  2. Collab Sheets
  3. Customer Churn Prediction System

- Mention MULTIPLE experiences if available
- Do not focus on only one project
- Do not focus on only one role
- Give balanced summaries

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
        max_tokens=900,
    )

    answer = response.choices[0].message.content

    # =========================
    # RETURN
    # =========================

    return {
        "response": answer
    }