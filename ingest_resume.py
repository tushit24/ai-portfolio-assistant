import chromadb
import uuid
import os

from pypdf import PdfReader


# ============================================================
# PATHS
# ============================================================

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

CHROMA_PATH = os.path.join(
    BASE_DIR,
    "chroma_db"
)

RESUME_PATH = os.path.join(
    BASE_DIR,
    "Tushit_Tiwari_Resume.pdf"
)


# ============================================================
# CHROMADB
# ============================================================

client = chromadb.PersistentClient(
    path=CHROMA_PATH
)


# ============================================================
# DELETE OLD COLLECTIONS
# ============================================================

COLLECTION_NAMES = [
    "projects",
    "certifications",
    "experience",
    "skills",
    "resume_collection"
]

print("\nRemoving old knowledge base...\n")

for name in COLLECTION_NAMES:

    try:

        client.delete_collection(name)

        print(f"  ✓ Deleted: {name}")

    except Exception:

        print(f"  - {name} not found")


# ============================================================
# CREATE COLLECTIONS
# ============================================================

projects_collection = client.get_or_create_collection(
    name="projects"
)

certifications_collection = client.get_or_create_collection(
    name="certifications"
)

experience_collection = client.get_or_create_collection(
    name="experience"
)

skills_collection = client.get_or_create_collection(
    name="skills"
)

resume_collection = client.get_or_create_collection(
    name="resume_collection"
)


# ============================================================
# LOAD ACTUAL RESUME PDF
# ============================================================

print("\nLoading latest resume PDF...")

if not os.path.exists(RESUME_PATH):

    raise FileNotFoundError(
        f"Resume not found at:\n{RESUME_PATH}"
    )


reader = PdfReader(RESUME_PATH)

resume_text = ""

for page_number, page in enumerate(reader.pages, start=1):

    extracted = page.extract_text()

    if extracted:

        resume_text += (
            f"\n--- Resume Page {page_number} ---\n"
        )

        resume_text += extracted


print(
    f"  ✓ Resume loaded successfully "
    f"({len(reader.pages)} pages)"
)

print(
    f"  ✓ Extracted {len(resume_text)} characters"
)


# ============================================================
# SMART RESUME CHUNKING
# ============================================================

def split_text(
    text,
    chunk_size=1200,
    overlap=150
):

    text = text.replace(
        "\r",
        "\n"
    )

    text = "\n".join(
        line.strip()
        for line in text.splitlines()
        if line.strip()
    )

    chunks = []

    start = 0

    while start < len(text):

        end = min(
            start + chunk_size,
            len(text)
        )

        chunk = text[start:end].strip()

        if chunk:

            chunks.append(chunk)

        if end >= len(text):

            break

        start = end - overlap

    return chunks


resume_chunks = split_text(
    resume_text
)


print(
    f"  ✓ Created {len(resume_chunks)} resume chunks"
)


# ============================================================
# STORE ACTUAL RESUME
# ============================================================

resume_collection.add(

    ids=[
        f"resume_{uuid.uuid4()}"
        for _ in resume_chunks
    ],

    documents=resume_chunks,

    metadatas=[
        {
            "source": "latest_resume_pdf",
            "type": "resume",
            "chunk_index": i
        }

        for i in range(len(resume_chunks))
    ]
)


print(
    f"  ✓ resume_collection: "
    f"{len(resume_chunks)} chunks"
)


# ============================================================
# STRUCTURED PROJECT DATA
# ============================================================

projects = [

    """
Project: AI Portfolio Assistant

Tech Stack:
React, FastAPI, ChromaDB, RAG, Groq LLM, Vercel, Render.

Description:
A full-stack RAG-powered portfolio chatbot designed to answer
questions about Tushit's education, skills, projects,
certifications and professional experience.

The system uses ChromaDB for semantic retrieval and Groq API
for LLM-based response generation.
""",

    """
Project: Spendy

Tech Stack:
Flutter, Dart, Firebase Firestore, Firebase Authentication,
Firebase Cloud Messaging, Cloud Functions, fl_chart.

Description:
A cross-platform expense splitting mobile application.

Features:
- Real-time Firestore synchronization
- Google OAuth
- Push notifications
- Spending analytics
- UPI deep linking
- Google Pay
- PhonePe
- Paytm
- Production release
""",

    """
Project: Collab Sheets

Tech Stack:
Next.js 14, TypeScript, Firebase Firestore, Vercel,
GitHub Actions, react-window.

Description:
A Google Sheets-inspired real-time collaborative spreadsheet
application.

Features:
- Multi-user editing
- Live presence
- Firestore synchronization
- Custom formula engine
- Dependency graph
- Circular dependency detection
- Cell virtualization
- CSV/JSON export
- Keyboard shortcuts
- Vercel deployment
- GitHub CI/CD
""",

    """
Project: VR Table Tennis Game

Tech Stack:
Unity, C#, SteamVR, OpenXR, Physics Engine.

Description:
An immersive virtual reality table tennis game with
realistic physics and an AI-controlled opponent.

Features:
- VR interaction
- Real-time physics
- Collision detection
- Finite State Machine AI
- Three difficulty levels
- SteamVR/OpenXR
"""
]


projects_collection.add(

    ids=[
        f"project_{uuid.uuid4()}"
        for _ in projects
    ],

    documents=projects,

    metadatas=[
        {
            "source": "structured_portfolio",
            "type": "project",
            "project_index": i
        }

        for i in range(len(projects))
    ]
)


print(
    f"  ✓ projects: {len(projects)} documents"
)


# ============================================================
# EXPERIENCE
# ============================================================

experience = [

    """
Experience:
MERN Stack Intern — AI & Full Stack

Organization:
Vicharanashala Lab for Education Design (VLED), IIT Ropar.

Work:
Full-stack development, AI integration, REST APIs,
RAG-based AI modules and educational technology platforms.
""",

    """
Experience:
Research Intern & SEO Strategist

Organization:
TheGeostrata, New Delhi.

Work:
SEO strategy, Google Analytics, Google Search Console,
research writing, content strategy and digital growth.
""",

    """
Experience:
Core Member — Design Team

Organization:
E-Cell VIT Bhopal University.

Work:
Marketing creatives, pitch decks, event branding,
UI/UX and digital design for entrepreneurship events.
"""
]


experience_collection.add(

    ids=[
        f"experience_{uuid.uuid4()}"
        for _ in experience
    ],

    documents=experience,

    metadatas=[
        {
            "source": "structured_portfolio",
            "type": "experience",
            "experience_index": i
        }

        for i in range(len(experience))
    ]
)


print(
    f"  ✓ experience: {len(experience)} documents"
)


# ============================================================
# CERTIFICATIONS
# ============================================================

certifications = [

    "AWS Certified Cloud Practitioner (CLF-C02)",

    "Google IT Support Professional Certificate",

    "MERN Full Stack Development — ETHNUS",

    "Deep Learning — NPTEL IIT Ropar",

    "Oracle Cloud AI Foundations",

    "Oracle Generative AI Professional",

    "Wipro Earthian Award",

    "Letter of Recommendation from the Defense Minister of India"
]


certifications_collection.add(

    ids=[
        f"cert_{uuid.uuid4()}"
        for _ in certifications
    ],

    documents=certifications,

    metadatas=[
        {
            "source": "structured_portfolio",
            "type": "certification",
            "certification_index": i
        }

        for i in range(len(certifications))
    ]
)


print(
    f"  ✓ certifications: "
    f"{len(certifications)} documents"
)


# ============================================================
# SKILLS
# ============================================================

skills = [

    """
Frontend:
React.js, Next.js 14, Flutter, HTML5, CSS3,
Tailwind CSS, Framer Motion.
""",

    """
Backend:
Node.js, Express.js, FastAPI, Django REST Framework,
REST API Design, Authentication, Authorization,
JWT, Google OAuth.
""",

    """
Databases and AI:
Firebase, MongoDB, MySQL, SQLite, AWS DynamoDB,
ChromaDB, TensorFlow, Scikit-learn, Pandas,
OpenCV, RAG, Vector Embeddings.
""",

    """
Cloud and DevOps:
AWS EC2, AWS S3, AWS DynamoDB, AWS IAM,
Docker, Git, CI/CD, Vercel, Render.
""",

    """
Programming Languages:
Java, C++, Python, JavaScript, TypeScript, Dart.
""",

    """
Other:
Unity Engine, REST APIs, real-time systems,
cloud infrastructure and deployment.
"""
]


skills_collection.add(

    ids=[
        f"skill_{uuid.uuid4()}"
        for _ in skills
    ],

    documents=skills,

    metadatas=[
        {
            "source": "structured_portfolio",
            "type": "skill",
            "skill_index": i
        }

        for i in range(len(skills))
    ]
)


print(
    f"  ✓ skills: {len(skills)} documents"
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n==============================================")
print("KNOWLEDGE BASE BUILT SUCCESSFULLY")
print("==============================================")

print(
    f"Projects:        {projects_collection.count()}"
)

print(
    f"Certifications:  {certifications_collection.count()}"
)

print(
    f"Experience:      {experience_collection.count()}"
)

print(
    f"Skills:          {skills_collection.count()}"
)

print(
    f"Resume PDF:      {resume_collection.count()} chunks"
)

print("\nResume source:")
print("  Tushit_Tiwari_Resume.pdf")

print("\nThe latest PDF is now the source of truth for resume data.")