"""
reingest_clean.py
-----------------
Drops and rebuilds ALL collections cleanly.
Run this ONCE to fix the polluted resume_collection.

Usage:
    python reingest_clean.py
"""

import chromadb
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CHROMA_PATH = os.path.join(BASE_DIR, "chroma_db")

client = chromadb.PersistentClient(path=CHROMA_PATH)

# ── Drop all existing collections ────────────────────────────────────────────
COLLECTION_NAMES = ["projects", "certifications", "experience", "skills", "resume_collection"]

print("Dropping existing collections...")
for name in COLLECTION_NAMES:
    try:
        client.delete_collection(name)
        print(f"  ✓ Dropped: {name}")
    except Exception:
        print(f"  - Not found (skipping): {name}")

# ── Helper ───────────────────────────────────────────────────────────────────

def upsert(collection_name: str, docs: list[dict]):
    col = client.get_or_create_collection(collection_name)
    if docs:
        col.upsert(
            ids=[d["id"] for d in docs],
            documents=[d["text"] for d in docs],
        )
    print(f"  ✓ {collection_name}: {len(docs)} chunks")

# ============================================================
# PROJECTS
# ============================================================

projects = [
    {
        "id": "proj_spendy",
        "text": """Project: Spendy
Type: Cross-platform Mobile Application
Priority: Highest
Production: Yes — Production APK released
Description: A cross-platform expense splitting mobile application built using Flutter and Firebase.
Tech Stack: Flutter, Dart, Firebase Firestore, Firebase Authentication, Firebase Cloud Messaging (FCM), Cloud Functions, fl_chart
Key Features:
- Architected real-time Firestore sync for live bill-splitting across devices
- Google OAuth via Firebase Auth and FCM push notifications through Cloud Functions
- Interactive spending analytics using fl_chart library
- UPI deep-link integration pre-filling recipient ID and exact amount for one-tap debt settlement (Google Pay, PhonePe, Paytm)
- Owned full deployment and production release lifecycle
-Can be dowloaded from "https://drive.google.com/drive/u/0/folders/1E8GOk3zyCwhcM57IgKx3zOEkpdQvFagL"""
    },
    {
        "id": "proj_collab_sheets",
        "text": """Project: Collab Sheets
Type: Real-Time Collaborative Web Application
Priority: Highest
Live URL: spreadsheet-app-ivory.vercel.app
Description: A multi-user Google Sheets-inspired collaborative spreadsheet web application.
Tech Stack: Next.js 14 (App Router), TypeScript, Firebase Firestore, Vercel, GitHub CI/CD, react-window
Key Features:
- Live presence indicators and real-time Firestore synchronization for multi-user collaboration
- Custom formula engine with dependency graph traversal and circular dependency detection
- Optimized rendering using react-window grid virtualization
- Drag-to-resize columns, Ctrl+B/I/U keyboard shortcuts, CSV and JSON export
- Deployed on Vercel with GitHub CI/CD pipeline
- Live at: spreadsheet-app-ivory.vercel.app"""
    },
    {
        "id": "proj_churn_prediction",
        "text": """Project: Customer Churn Prediction System
Type: Machine Learning / Data Science Project
Description: An end-to-end machine learning pipeline to predict customer churn using the Kaggle Telco dataset.
Tech Stack: Python, Scikit-learn, SMOTE (imbalanced-learn), Pandas, Streamlit
Key Features:
- Built on Kaggle Telco dataset with 7,043 records
- Applied SMOTE to handle class imbalance in churn data
- Feature engineering from contract and billing data
- Deployed a Streamlit dashboard supporting bulk CSV prediction uploads"""
    },
]

# ============================================================
# CERTIFICATIONS & HONORS
# ============================================================

certifications = [
    {
        "id": "cert_google_it",
        "text": """Certification: Google IT Support Professional
Issuer: Google
Description: Covers IT support fundamentals, networking, operating systems, system administration, and troubleshooting."""
    },
    {
        "id": "cert_oracle_ai_foundations",
        "text": """Certification: Oracle Cloud AI Foundations
Issuer: Oracle
Description: Demonstrates understanding of AI fundamentals and cloud computing on Oracle Cloud Infrastructure."""
    },
    {
        "id": "cert_oracle_genai",
        "text": """Certification: Oracle Generative AI Professional
Issuer: Oracle
Description: Professional-level certification covering generative AI concepts, large language models, and Oracle AI services."""
    },
    {
        "id": "cert_mern",
        "text": """Certification: MERN Full Stack Development
Issuer: ETHNUS
Description: Full stack development using MongoDB, Express.js, React.js, and Node.js."""
    },
    {
        "id": "cert_deep_learning",
        "text": """Certification: Deep Learning
Issuer: NPTEL, IIT Ropar
Description: Completed NPTEL deep learning course covering neural networks, CNNs, and modern machine learning techniques."""
    },
    {
        "id": "honor_wipro_earthian",
        "text": """Honor / Award: Wipro Earthian Award
Issuer: Wipro
Description: Received the Wipro Earthian Award recognizing innovation and sustainability-focused thinking."""
    },
    {
        "id": "honor_defense_minister_lor",
        "text": """Honor: Letter of Recommendation from the Defense Minister of India
Description: Received a Letter of Recommendation from the Defense Minister of India, recognizing achievements and contributions."""
    },
]

# ============================================================
# EXPERIENCE
# ============================================================

experience = [
    {
     "id": "exp_geostrata",
        "text": """Experience: Research Intern and SEO Analyst
Organization: TheGeostrata — New Delhi (Remote)
Duration: April 2024 – October 2024
Professional Experience Summary:
Worked as a Research Intern and SEO Designer for a geopolitics and international affairs research platform.
Type: Remote internship
Responsibilities:
- Designed and executed SEO strategy for a geopolitics research platform
- Tracked organic performance using Google Analytics and Search Console
- Authored research articles on geopolitics and international affairs
- Managed content strategy and publication pipeline
Skills Demonstrated:
SEO, research writing, analytics, content strategy, digital branding, technical communication
"""   
    },
    {
        "id": "exp_ecell_vit",
        "text": """Role: Core Member, Design Team
Organization: E-Cell VIT Bhopal
Duration: January 2025 – Present
Responsibilities:
- Led frontend development and UI/UX design for the E-Summit 2025 website (1,000+ attendees)
- Owned full deployment, post-launch iteration, and digital brand identity across channels
- Worked on digital branding tasks and SEO optimization"""
    },
]

# ============================================================
# SKILLS
# ============================================================

skills = [
    {
        "id": "skills_languages",
        "text": """Programming Languages:
Python, JavaScript, TypeScript, Java, C++, Dart"""
    },
    {
        "id": "skills_frontend",
        "text": """Frontend Technologies:
React.js, Next.js 14 (App Router), Flutter, HTML5, CSS3, Tailwind CSS, TypeScript"""
    },
    {
        "id": "skills_backend",
        "text": """Backend Technologies:
Node.js, Express.js, Django REST Framework, REST API Design,
Authentication and Authorization: Firebase Auth, JWT, Google OAuth"""
    },
    {
        "id": "skills_db_cloud",
        "text": """Databases and Cloud:
Firebase Firestore, Firebase Cloud Functions, Firebase Cloud Messaging (FCM),
MongoDB, SQLite, AWS EC2, AWS S3, Vercel deployment"""
    },
    {
        "id": "skills_devops",
        "text": """DevOps and Tools:
Docker, Git, GitHub, CI/CD pipelines, Linux environments, GitHub Actions"""
    },
    {
        "id": "skills_ai_ml",
        "text": """AI and Machine Learning:
TensorFlow, Scikit-learn, Pandas, OpenCV, SMOTE (imbalanced-learn),
data preprocessing pipelines, feature engineering, Streamlit"""
    },
]

# ============================================================
# GENERAL / BIO  — structured only, NO prose from profile.txt
# ============================================================

general = [
    {
        "id": "bio_tushit",
        "text": """Name: Tushit Tiwari
Contact: +91-9555672098 | rishitiwariofficial@gmail.com
Education: B.Tech, Computer Science and Engineering — Specialization: E-Commerce Technology
University: VIT Bhopal University
Duration: August 2023 – May 2027
Year: Third year (2023–2027)
CGPA: 8.0 / 10
School: City Montessori School, Lucknow — High School: 93.8%, Intermediate: 86.25%

Summary:
Full Stack Software Engineer (in training) with production experience building and deploying
scalable web and mobile applications using React, Next.js, Node.js, Flutter, and Firebase.
Skilled in REST API design, real-time systems, authentication, state management, and
end-to-end deployment on AWS and Vercel. Certified by Google, Oracle, and NPTEL IIT Ropar.

Career Goals:
Aiming to become a highly skilled software engineer and AI-focused full stack developer
building scalable and impactful products. Interested in full stack development,
cloud infrastructure, automation, machine learning, DevOps, and real-time collaborative systems.
Open to opportunities in software engineering, full stack development, AI engineering,
cloud engineering, DevOps, backend development, frontend engineering, and product-focused roles.

Background:
Currently a student and early-career developer. Experience comes from academic projects,
internships, self-learning, research work, and hands-on personal development projects.

Interests outside tech:
Geopolitics, strategy, design, writing, and emerging technology trends."""
    },
]

# ── Run ingestion ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print("\nIngesting clean resume data into ChromaDB...")
    upsert("projects",          projects)           # 3  docs
    upsert("certifications",    certifications)     # 7  docs
    upsert("experience",        experience)         # 2  docs
    upsert("skills",            skills)             # 6  docs
    upsert("resume_collection", general + projects + certifications + experience + skills)  # 19 docs

    print("\nDone! Expected counts:")
    print("  projects: 3 | certifications: 7 | experience: 2 | skills: 6 | general: 19")
    print("\nNow restart uvicorn and hit /debug to verify.")