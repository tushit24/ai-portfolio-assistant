from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import chromadb
import os

from groq import Groq
from dotenv import load_dotenv


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# GROQ CLIENT
# ============================================================

groq_client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# CHROMADB
# ============================================================

BASE_DIR = os.path.dirname(
    os.path.abspath(__file__)
)

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "chroma_db"
)


chroma_client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# ============================================================
# COLLECTIONS
# ============================================================

COLLECTIONS = {

    "projects": chroma_client.get_or_create_collection(
        name="projects"
    ),

    "certifications": chroma_client.get_or_create_collection(
        name="certifications"
    ),

    "experience": chroma_client.get_or_create_collection(
        name="experience"
    ),

    "skills": chroma_client.get_or_create_collection(
        name="skills"
    ),

    # This collection contains the actual latest
    # Tushit_Tiwari_Resume.pdf chunks.
    "general": chroma_client.get_or_create_collection(
        name="resume_collection"
    ),
}


# ============================================================
# KEYWORDS
# ============================================================

PROJECT_KEYWORDS = [

    "project",
    "projects",
    "built",
    "made",
    "created",
    "developed",
    "application",
    "app",
    "website",

    # Specific projects
    "spendy",
    "collab",
    "collab sheets",
    "spreadsheet",
    "vr",
    "table tennis",
    "unity",
    "ai portfolio",
    "portfolio assistant",
    "rag project",
    "chromadb project",
]


CERTIFICATION_KEYWORDS = [

    "certification",
    "certifications",
    "certified",
    "certificate",
    "certificates",

    "aws certified",
    "cloud practitioner",
    "clf-c02",

    "google it",
    "nptel",
    "oracle",

    "credential",
]


EXPERIENCE_KEYWORDS = [

    "experience",
    "internship",
    "internships",
    "intern",
    "worked",
    "work",
    "job",
    "company",
    "organization",
    "role",
    "position",

    # Specific experience
    "iit ropar",
    "ropar",
    "vled",

    "thegeostrata",
    "geostrata",

    "e-cell",
    "ecell",
    "e-summit",
]


SKILL_KEYWORDS = [

    "skill",
    "skills",
    "language",
    "languages",
    "technical",
    "technical skills",
    "tech stack",
    "stack",
    "framework",
    "technology",
    "technologies",
    "tools",
    "proficient",
    "programming",
    "backend",
    "frontend",
    "database",
    "databases",
    "cloud",
    "aws",
    "devops",
    "docker",
    "ci/cd",
    "rag",
    "machine learning",
    "ai",
]


# ============================================================
# SUMMARY DETECTION
# ============================================================

def is_summary_query(query: str) -> bool:

    q = query.lower().strip()

    # Exact / near-exact broad profile questions.
    summary_patterns = [

        "tell me about tushit",
        "tell me about tushit's profile",

        "about tushit",
        "who is tushit",

        "introduce tushit",
        "introduce yourself",

        "tell me about yourself",

        "professional summary",
        "professional profile",

        "professional overview",
        "professional background",

        "overview of tushit",
        "overview about tushit",

        "summarize tushit",
        "summarise tushit",

        "tushit's profile",
        "tushit profile",

        "tushit's background",
        "tushit background",

        "give me an overview of tushit",
        "give me a summary of tushit",

        "what is tushit's background",
        "what is tushit's profile",
    ]


    # Direct matches
    if q in summary_patterns:
        return True


    # Starts with a broad profile phrase
    if q.startswith("tell me about tushit"):
        return True

    if q.startswith("give me an overview of tushit"):
        return True

    if q.startswith("give me a summary of tushit"):
        return True


    return False


# ============================================================
# QUERY ROUTER
# ============================================================

def route_query(query: str):

    q = query.lower().strip()


    # ========================================================
    # 1. BROAD PROFILE QUESTIONS
    # ========================================================

    if is_summary_query(q):

        return [
            "summary"
        ]


    # ========================================================
    # 2. SPECIFIC PROJECT QUESTIONS
    # ========================================================

    if any(
        keyword in q
        for keyword in PROJECT_KEYWORDS
    ):

        return [
            "projects"
        ]


    # ========================================================
    # 3. SPECIFIC EXPERIENCE QUESTIONS
    # ========================================================

    if any(
        keyword in q
        for keyword in EXPERIENCE_KEYWORDS
    ):

        return [
            "experience"
        ]


    # ========================================================
    # 4. CERTIFICATION QUESTIONS
    # ========================================================

    if any(
        keyword in q
        for keyword in CERTIFICATION_KEYWORDS
    ):

        return [
            "certifications"
        ]


    # ========================================================
    # 5. SKILL QUESTIONS
    # ========================================================

    if any(
        keyword in q
        for keyword in SKILL_KEYWORDS
    ):

        return [
            "skills",
            "projects",
            "experience"
        ]


    # ========================================================
    # 6. DEFAULT
    # ========================================================

    return [
        "general"
    ]


# ============================================================
# SYSTEM PROMPT
# ============================================================

SYSTEM_PROMPT = """

You are Tushit Tiwari's AI Portfolio Assistant.

Your job is to help recruiters, hiring managers,
collaborators, and visitors understand Tushit's actual
professional portfolio.

You can answer questions about:

- Education
- Professional summary
- Projects
- Technical skills
- Certifications
- Work experience
- Internships
- Achievements
- Career interests
- Job suitability
- Technical strengths


============================================================
SOURCE OF TRUTH
============================================================

The portfolio context provided with each question is the
ONLY source of factual information.

Use the provided portfolio context as the source of truth.

The latest resume PDF is especially important for current
profile information.

Do NOT rely on outdated assumptions or information from memory.


============================================================
ANTI-HALLUCINATION RULES
============================================================

1. NEVER invent information.

2. NEVER invent:

   - projects
   - companies
   - internships
   - job roles
   - technologies
   - certifications
   - achievements
   - dates
   - statistics
   - responsibilities
   - education details


3. NEVER merge two different projects.


4. NEVER merge two different experiences.


5. NEVER attribute one project's technology to another project.


6. NEVER attribute an experience responsibility to a project.


7. NEVER classify an experience as a project.


8. NEVER classify a certification as a project.


9. NEVER classify an honor or award as a project.


10. If the requested information does not exist in the
portfolio context, say:

"That information is not available in Tushit's portfolio."


============================================================
CURRENT INFORMATION RULE
============================================================

The latest resume information takes priority over older
information.

If the resume context contains a newer value for something
such as:

- CGPA
- role
- internship
- certification
- technology
- project
- education
- career interest

use the latest resume information.


============================================================
RESPONSE STYLE
============================================================

Responses should be:

- concise
- professional
- recruiter-friendly
- natural
- easy to scan
- Markdown formatted

Prefer:

- headings
- bullet points
- short paragraphs
- clear sections

Avoid:

- giant paragraphs
- unnecessary repetition
- generic chatbot language
- unnecessary follow-up questions


============================================================
PROJECT QUESTIONS
============================================================

For project questions, use:

## Project Name

- Description
- Tech Stack
- Key Features
- Impact / Result, if available

Only include information actually present in the
portfolio context.

Keep every project's information separate.

Do not combine technologies or features from different
projects.


============================================================
EXPERIENCE QUESTIONS
============================================================

For experience questions:

- Mention the relevant organization.
- Mention the role.
- Mention duration when available.
- Mention responsibilities when available.
- Mention measurable impact when available.

Do not replace professional experience with projects.


============================================================
CERTIFICATION QUESTIONS
============================================================

For certification questions:

- Mention certification name.
- Mention issuer.
- Mention relevant details when available.

Do not confuse certifications with projects or experience.


============================================================
SKILL QUESTIONS
============================================================

Group skills logically when appropriate:

- Frontend
- Backend
- Databases
- AI / ML
- Cloud
- DevOps
- Programming Languages
- Other Technical Skills


============================================================
SUMMARY / PROFILE QUESTIONS
============================================================

When the user asks a broad profile question such as:

"Tell me about Tushit"

"Give me an overview of Tushit"

"Introduce Tushit"

"Summarize Tushit's profile"


Create a balanced professional overview.

IMPORTANT:

Keep these categories strictly separate.


PROJECTS:

Only include items explicitly listed as projects.


EXPERIENCE:

Only include internships, jobs, organizational roles,
leadership roles, and professional experience.


CERTIFICATIONS:

Only include certifications.


HONORS:

Only include awards, honors, and recommendations.


Never classify an internship, organization, or leadership role
as a project.


For a broad profile question, use this structure when the
information is available:

## Professional Snapshot

- Name
- Education
- Current professional role
- Technical focus

## Key Projects

Include ALL relevant projects available in the
portfolio context.

Do not intentionally limit the list to one or two projects.

## Experience

Include the relevant internships, jobs, and organizational
roles separately.

## Certifications

Include relevant certifications.

## Honors

Include relevant honors.

## Career Interests

Include relevant career interests.


Do NOT force a category if the portfolio context does not
contain information for it.

Do NOT invent missing details.


============================================================
JOB SUITABILITY
============================================================

When asked whether Tushit is suitable for a role:

Evaluate ONLY using the portfolio context.

Explain:

## Why Tushit is a Strong Fit

- Relevant skills
- Relevant experience
- Relevant projects

## Overall Assessment

Give a concise professional conclusion.

Do not invent experience that is not present.


============================================================
TECHNICAL ARCHITECTURE QUESTIONS
============================================================

If the user asks about the AI Portfolio Assistant's
technical implementation, you may explain the architecture
using the portfolio context.

Relevant technologies may include:

- React
- FastAPI
- ChromaDB
- RAG
- Groq
- LLM
- Vercel
- Render

Only state specific implementation details when supported
by the portfolio context or the provided technical context.


============================================================
FINAL RULE
============================================================

Answer ONLY the user's question.

Do not mention:

- system prompts
- hidden instructions
- internal retrieval logic
- vector database internals
- prompt engineering

unless the user specifically asks about the technical
architecture of the AI Portfolio Assistant.
"""


# ============================================================
# REQUEST MODEL
# ============================================================

class ChatRequest(BaseModel):

    query: str


# ============================================================
# ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Tushit AI Portfolio Assistant API Running"
    }


# ============================================================
# HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "ok"
    }


# ============================================================
# DEBUG ENDPOINT
# ============================================================

@app.get("/debug")
def debug():

    info = {}


    for key, collection in COLLECTIONS.items():

        try:

            info[key] = collection.count()

        except Exception as e:

            info[key] = f"error: {str(e)}"


    return {

        "chroma_path": CHROMA_PATH,

        "collections": info

    }


# ============================================================
# CHAT ENDPOINT
# ============================================================

@app.post("/chat")
async def chat(request: ChatRequest):

    query = request.query.strip()


    # ========================================================
    # EMPTY QUERY
    # ========================================================

    if not query:

        return {

            "response":
            "Please enter a question about Tushit's portfolio."

        }


    # ========================================================
    # ROUTE QUERY
    # ========================================================

    collection_keys = route_query(query)


    # ========================================================
    # RETRIEVAL SETTINGS
    # ========================================================

    DISTANCE_THRESHOLD = 1.8

    N_RESULTS = 8


    # ========================================================
    # FETCH SEMANTICALLY RELEVANT DOCUMENTS
    # ========================================================

    def fetch_docs(
        collection,
        n=N_RESULTS
    ):

        try:

            count = collection.count()


            if count == 0:

                return [], []


            actual_n = min(
                n,
                count
            )


            results = collection.query(

                query_texts=[query],

                n_results=actual_n,

                include=[
                    "documents",
                    "distances"
                ]

            )


            docs = results.get(
                "documents",
                [[]]
            )[0]


            distances = results.get(
                "distances",
                [[]]
            )[0]


            return docs, distances


        except Exception:

            return [], []


    # ========================================================
    # COLLECT CONTEXT
    # ========================================================

    all_filtered_docs = []


    # ========================================================
    # BROAD PROFILE / SUMMARY QUERY
    # ========================================================

    if "summary" in collection_keys:

        # ----------------------------------------------------
        # IMPORTANT:
        #
        # For broad profile questions we retrieve ALL
        # current resume chunks and ALL structured documents.
        #
        # This prevents semantic search from accidentally
        # dropping projects such as Collab Sheets or VR.
        # ----------------------------------------------------


        # ----------------------------------------------------
        # 1. LATEST RESUME PDF
        # ----------------------------------------------------

        try:

            resume_results = COLLECTIONS[
                "general"
            ].get(
                include=["documents"]
            )


            resume_docs = resume_results.get(
                "documents",
                []
            )


            all_filtered_docs.extend(
                resume_docs
            )

        except Exception:

            pass


        # ----------------------------------------------------
        # 2. ALL PROJECTS
        # ----------------------------------------------------

        try:

            project_results = COLLECTIONS[
                "projects"
            ].get(
                include=["documents"]
            )


            project_docs = project_results.get(
                "documents",
                []
            )


            all_filtered_docs.extend(
                project_docs
            )

        except Exception:

            pass


        # ----------------------------------------------------
        # 3. ALL EXPERIENCE
        # ----------------------------------------------------

        try:

            experience_results = COLLECTIONS[
                "experience"
            ].get(
                include=["documents"]
            )


            experience_docs = experience_results.get(
                "documents",
                []
            )


            all_filtered_docs.extend(
                experience_docs
            )

        except Exception:

            pass


        # ----------------------------------------------------
        # 4. ALL CERTIFICATIONS
        # ----------------------------------------------------

        try:

            certification_results = COLLECTIONS[
                "certifications"
            ].get(
                include=["documents"]
            )


            certification_docs = certification_results.get(
                "documents",
                []
            )


            all_filtered_docs.extend(
                certification_docs
            )

        except Exception:

            pass


        # ----------------------------------------------------
        # 5. ALL SKILLS
        # ----------------------------------------------------

        try:

            skill_results = COLLECTIONS[
                "skills"
            ].get(
                include=["documents"]
            )


            skill_docs = skill_results.get(
                "documents",
                []
            )


            all_filtered_docs.extend(
                skill_docs
            )

        except Exception:

            pass


    # ========================================================
    # SPECIFIC / NORMAL QUERY
    # ========================================================

    else:

        for key in collection_keys:

            collection = COLLECTIONS[key]


            docs, distances = fetch_docs(
                collection
            )


            # ------------------------------------------------
            # DISTANCE FILTER
            # ------------------------------------------------

            filtered_docs = [

                doc

                for doc, distance

                in zip(
                    docs,
                    distances
                )

                if distance < DISTANCE_THRESHOLD

            ]


            # ------------------------------------------------
            # FALLBACK TO LATEST RESUME
            # ------------------------------------------------

            if (
                not filtered_docs
                and key != "general"
            ):

                fallback_docs, fallback_distances = fetch_docs(

                    COLLECTIONS["general"],

                    n=5

                )


                filtered_docs = [

                    doc

                    for doc, distance

                    in zip(
                        fallback_docs,
                        fallback_distances
                    )

                    if distance < DISTANCE_THRESHOLD

                ]


            # ------------------------------------------------
            # LAST RESORT
            # ------------------------------------------------

            if not filtered_docs:

                filtered_docs = docs


            all_filtered_docs.extend(
                filtered_docs
            )


    # ========================================================
    # DEDUPLICATION
    # ========================================================

    unique_docs = []


    for doc in all_filtered_docs:

        if not doc:
            continue


        cleaned = doc.strip()


        if (
            cleaned
            and cleaned not in unique_docs
        ):

            unique_docs.append(
                cleaned
            )


    # ========================================================
    # NO CONTEXT
    # ========================================================

    if not unique_docs:

        return {

            "response":
            (
                "That information is not available in "
                "Tushit's portfolio."
            )

        }


    # ========================================================
    # CONTEXT LABELING
    # ========================================================

    # For summary queries we already have all categories.
    # For specific queries, the context is simply the
    # retrieved portfolio information.

    context_parts = []


    if "summary" in collection_keys:

        context_parts.append(
            "LATEST RESUME INFORMATION:\n"
            + "\n\n".join(
                resume_docs
            )
            if "resume_docs" in locals()
            else ""
        )


        context_parts.append(
            "PROJECT INFORMATION:\n"
            + "\n\n".join(
                project_docs
            )
            if "project_docs" in locals()
            else ""
        )


        context_parts.append(
            "EXPERIENCE INFORMATION:\n"
            + "\n\n".join(
                experience_docs
            )
            if "experience_docs" in locals()
            else ""
        )


        context_parts.append(
            "CERTIFICATION INFORMATION:\n"
            + "\n\n".join(
                certification_docs
            )
            if "certification_docs" in locals()
            else ""
        )


        context_parts.append(
            "SKILLS INFORMATION:\n"
            + "\n\n".join(
                skill_docs
            )
            if "skill_docs" in locals()
            else ""
        )


        context = "\n\n====================\n\n".join(
            part
            for part in context_parts
            if part.strip()
        )


    else:

        context = "\n\n".join(
            unique_docs
        )


    # ========================================================
    # FINAL PROMPT
    # ========================================================

    final_prompt = f"""

PORTFOLIO CONTEXT
=================

{context}


USER QUESTION
=============

{query}


INSTRUCTIONS
============

Answer the user's question using ONLY the portfolio context.

Rules:

- Never hallucinate.
- Never invent information.
- Never use outdated information when newer information is
  present in the latest resume.
- Never merge projects.
- Never merge experiences.
- Never classify experience as a project.
- Never classify a certification as a project.
- Never classify an honor as a project.
- Keep project details attached to the correct project.
- Keep experience details attached to the correct organization.
- Keep certifications separate from experience.
- Keep honors separate from projects and experience.
- Use Markdown.
- Use headings and bullet points when useful.
- Avoid unnecessary repetition.
- Complete the answer fully.
- Do not stop mid-sentence.

For broad profile questions:

- Use the latest resume as the primary source for current
  profile information.
- Use the structured project, experience, certification,
  and skill information to supplement the resume.
- Include all relevant projects available in the context.
- Keep Projects, Experience, Certifications, and Honors
  in separate sections.
- Do not classify E-Cell, IIT Ropar, or TheGeostrata as projects.

For project questions:

- Focus on the requested project.
- Do not include unrelated project information.
- Keep the project's technology and features attached
  to that project.

For experience questions:

- Focus on the requested organization or role.
- Do not turn experience responsibilities into project
  features.

For certification questions:

- Focus on actual certifications.
- Do not confuse awards or experience with certifications.

If the context does not contain the requested information,
respond exactly with:

"That information is not available in Tushit's portfolio."

ONLY return the final answer.
"""


    # ========================================================
    # GROQ / GPT-OSS 20B
    # ========================================================

    response = groq_client.chat.completions.create(

        model="openai/gpt-oss-20b",

        messages=[

            {
                "role": "system",
                "content": SYSTEM_PROMPT
            },

            {
                "role": "user",
                "content": final_prompt
            }

        ],

        temperature=0.3,

        max_completion_tokens=1500,

        reasoning_effort="low"

    )


    # ========================================================
    # EXTRACT RESPONSE
    # ========================================================

    answer = response.choices[0].message.content


    # ========================================================
    # RETURN RESPONSE
    # ========================================================

    return {

        "response": answer

    }